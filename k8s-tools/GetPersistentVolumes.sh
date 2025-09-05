POD=a9nfdzwpd7d47vxpsmj7-n0-0
NS=aione-staging

for pvc in $(kubectl get pod "$POD" -n "$NS" \
  -o jsonpath='{range .spec.volumes[?(@.persistentVolumeClaim)]}{.persistentVolumeClaim.claimName}{"\n"}{end}'); do
  pv=$(kubectl get pvc "$pvc" -n "$NS" -o jsonpath='{.spec.volumeName}')
  echo "PVC: $pvc  PV: $pv"
  kubectl get pv "$pv" -o jsonpath='  volumeHandle: {.spec.csi.volumeHandle}{"\n"}  imageName: {.spec.csi.volumeAttributes.imageName}{"\n"}  pool: {.spec.csi.volumeAttributes.pool}{"\n"}'
  echo
done
