### Now try to get the serial number information of Module and Base board
cvm_addr=0x50
cvb_addr=0x56
for I in $cvm_addr $cvb_addr ; do
  if [ "$I" = "$cvm_addr" ] ; then
    phrase=`echo "Serial Number of Module"`
  else
    phrase=`echo "Serial Number for Base board"`
  fi
  # echo $phrase
  # First get the CVM serial number
  mapfile -t sn_lines < <( i2cdump -f -y -r 74-86 0 $I b )

  len=${#sn_lines[@]}
  if [ "$len" -ne "3" ]; then
          echo "FAILED to get $phrase!!"
          echo "EEPROM content:"
          i2cdump -f -y 0 $I b
  else 
  sn_str1=$(echo ${sn_lines[1]} | rev | cut -d' ' -f1 | rev)
  sn_str2=$(echo ${sn_lines[2]} | rev | cut -d' ' -f1 | rev)
  sn_str=$sn_str1$sn_str2
  echo "$phrase is $sn_str"
  fi
done

