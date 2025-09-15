#!/bin/bash

# 自动化节点重启脚本
# 功能：重启指定的单个节点，确保Ceph集群健康状态
# 用法：./auto-restart-nodes.sh <节点名称>
# 作者：系统管理员
# 日期：2025-09-15

# 配置文件路径
HOST_FILE="host.txt"
RESTART_SCRIPT="restart.sh"
LOG_FILE="restart-$(date +%Y%m%d_%H%M%S).log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO $(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS $(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING $(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR $(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

# 检查Ceph集群状态
check_ceph_status() {
    log_info "检查Ceph集群状态..."
    local status=$(ceph health detail 2>/dev/null | head -1)
    if echo "$status" | grep -q "HEALTH_OK"; then
        log_success "Ceph集群状态正常: $status"
        return 0
    else
        log_warning "Ceph集群状态异常: $status"
        return 1
    fi
}

# 等待Ceph状态恢复正常
wait_for_ceph_ok() {
    local max_wait=$1
    local wait_count=0
    
    log_info "等待Ceph集群状态恢复正常，最大等待时间: ${max_wait}秒"
    
    while [ $wait_count -lt $max_wait ]; do
        if check_ceph_status > /dev/null 2>&1; then
            log_success "Ceph集群状态已恢复正常"
            return 0
        fi
        
        sleep 10
        wait_count=$((wait_count + 10))
        log_info "等待中... (${wait_count}/${max_wait}秒)"
    done
    
    log_error "等待超时，Ceph集群状态未能在${max_wait}秒内恢复正常"
    return 1
}

# 设置Ceph恢复模式
set_ceph_recovery() {
    local action=$1
    
    if [ "$action" = "disable" ]; then
        log_info "设置Ceph OSD不进行数据恢复..."
        ceph osd set norecover
        if [ $? -eq 0 ]; then
            log_success "已设置 norecover 标志"
        else
            log_error "设置 norecover 标志失败"
            return 1
        fi
    elif [ "$action" = "enable" ]; then
        log_info "恢复Ceph OSD数据恢复功能..."
        ceph osd unset norecover
        if [ $? -eq 0 ]; then
            log_success "已取消 norecover 标志"
        else
            log_error "取消 norecover 标志失败"
            return 1
        fi
    fi
    return 0
}

# 重启单个节点
restart_node() {
    local hostname=$1
    
    log_info "准备重启节点: $hostname"
    
    # 检查节点是否已经重启过
    if grep -q "^$hostname.*已重启" "$HOST_FILE"; then
        log_warning "节点 $hostname 已经重启过，跳过"
        return 0
    fi
    
    # 检查restart.sh脚本是否存在
    if [ ! -f "$RESTART_SCRIPT" ]; then
        log_error "重启脚本 $RESTART_SCRIPT 不存在"
        return 1
    fi
    
    # 用户确认
    echo
    log_warning "即将重启节点: $hostname"
    read -p "确认要重启此节点吗？(y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "用户取消重启节点 $hostname"
        return 0
    fi
    
    # 设置不进行数据恢复
    if ! set_ceph_recovery "disable"; then
        log_error "设置norecover失败，停止重启操作"
        return 1
    fi
    
    # 执行节点重启
    log_info "开始重启节点 $hostname..."
    bash "$RESTART_SCRIPT" "$hostname"
    restart_result=$?
    
    if [ $restart_result -eq 0 ]; then
        log_success "节点 $hostname 重启完成"
    else
        log_error "节点 $hostname 重启失败"
        # 即使重启失败也要恢复recover设置
        set_ceph_recovery "enable"
        return 1
    fi
    
    # 恢复数据恢复功能
    log_info "等待30秒后恢复数据恢复功能..."
    sleep 30
    
    if ! set_ceph_recovery "enable"; then
        log_error "恢复数据恢复功能失败"
        return 1
    fi
    
    # 等待Ceph状态恢复
    log_info "等待Ceph集群状态恢复..."
    if wait_for_ceph_ok 300; then
        log_success "节点 $hostname 重启成功，Ceph集群状态正常"
        # 更新host.txt文件，标记为已重启
        sed -i "s/^$hostname$/$hostname 已重启 $(date '+%Y-%m-%d %H:%M:%S')/" "$HOST_FILE"
        log_success "已更新 $hostname 状态为已重启"
        return 0
    else
        log_error "节点 $hostname 重启后，Ceph集群状态未能恢复正常"
        return 1
    fi
}

# 显示使用说明
show_usage() {
    echo "用法: $0 <节点名称>"
    echo ""
    echo "参数说明:"
    echo "  <节点名称>    要重启的节点名称，必须在 $HOST_FILE 文件中存在"
    echo ""
    echo "示例:"
    echo "  $0 dc2-node20"
    echo ""
    echo "功能说明:"
    echo "  - 检查Ceph集群状态是否正常"
    echo "  - 设置norecover防止数据重平衡"
    echo "  - 重启指定节点"
    echo "  - 恢复数据恢复功能"
    echo "  - 等待Ceph集群状态恢复正常"
    echo "  - 记录重启状态到 $HOST_FILE"
    echo ""
}

# 检查节点是否在host.txt中存在
check_node_exists() {
    local node_name=$1
    if ! grep -q "^$node_name" "$HOST_FILE"; then
        log_error "节点 $node_name 不在主机列表文件 $HOST_FILE 中"
        log_info "可用的节点列表:"
        grep -v "^#" "$HOST_FILE" | grep -v "^$" | awk '{print "  " $1}' | tee -a "$LOG_FILE"
        return 1
    fi
    return 0
}

# 主函数
main() {
    local target_node=$1
    
    # 检查参数
    if [ -z "$target_node" ]; then
        echo "错误: 缺少节点名称参数"
        echo ""
        show_usage
        exit 1
    fi
    
    echo
    log_info "=========================================="
    log_info "      自动化节点重启脚本开始执行"
    log_info "      目标节点: $target_node"
    log_info "=========================================="
    echo
    
    # 检查必要文件是否存在
    if [ ! -f "$HOST_FILE" ]; then
        log_error "主机列表文件 $HOST_FILE 不存在"
        exit 1
    fi
    
    if [ ! -f "$RESTART_SCRIPT" ]; then
        log_error "重启脚本 $RESTART_SCRIPT 不存在"
        exit 1
    fi
    
    # 检查节点是否在列表中
    if ! check_node_exists "$target_node"; then
        exit 1
    fi
    
    # 检查初始Ceph状态
    log_info "检查初始Ceph集群状态..."
    if ! check_ceph_status; then
        log_error "Ceph集群状态异常，请先修复后再执行重启操作"
        exit 1
    fi
    
    # 重启指定节点
    echo
    log_info "---------- 开始重启节点 $target_node ----------"
    
    if restart_node "$target_node"; then
        log_success "节点 $target_node 重启成功"
        
        # 最终Ceph状态检查
        log_info "执行最终Ceph集群状态检查..."
        check_ceph_status
        
        log_info "=========================================="
        log_info "          重启操作完成"
        log_info "=========================================="
        log_success "节点 $target_node 重启成功"
        log_info "详细日志已保存到: $LOG_FILE"
        exit 0
    else
        log_error "节点 $target_node 重启失败"
        
        # 最终Ceph状态检查
        log_info "执行最终Ceph集群状态检查..."
        check_ceph_status
        
        log_info "=========================================="
        log_info "          重启操作完成"
        log_info "=========================================="
        log_error "节点 $target_node 重启失败"
        log_info "详细日志已保存到: $LOG_FILE"
        exit 1
    fi
}

# 脚本入口点
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi