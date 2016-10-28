#! /bin/bash
### BEGIN INIT INFO
# Provides:          AlexaBeagleBone
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: AlexaBeagleBone Service
# Description:       Start / Stop AlexaBeagleBone Service
### END INIT INFO

exec > /var/log/alexa.log 2>&1 
case "$1" in

start)
	echo "AlexaBeagleBone waiting for 60 seconds to acquire network address"    
	sleep 60    # HACK: this is lazy- there are better ways to do this.
	echo "Starting Alexa..."    
	sudo python $HOME/AlexaBeagleBone/main.py &

;;

stop)
    echo "Stopping Alexa.."
    pkill -SIGINT ^main.py$
;;

restart|force-reload)
        echo "Restarting Alexa.."
        $0 stop
        sleep 2
        $0 start
        echo "Restarted."
;;
*)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
esac
