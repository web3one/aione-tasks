dmsetup ls | grep "test--vg" | cut -f1 | while read device; do     dmsetup remove "$device" 2>/dev/null || true; done
