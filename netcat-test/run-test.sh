if echo $STRING | nc $ADDRESS $PORT | grep -q $STRING; then
	echo OK
else
	echo MESSAGE MISMATCH
fi
