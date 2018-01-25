#!/bin/sh

option1="$1"
option2="$2" 

case $option1 in
    "genargus")
        echo "Deleting existing argus files in 'flows/argus/'";
        rm flows/argus/*.argus;
        for capfile in caps/*.pcapng; do
            filename=$(basename "$capfile");
            echo "Generating argus flows for $filename from pcap $capfile";
            argus -r "$capfile" -mAJZR -w flows/argus/"${filename%.*}".argus;
        done
        ;;

    "readargus")
        echo "Writing argus files to csv format";
        rm flows/argus/*.csv;
        for argusfile in flows/argus/*.argus; do
            filename=$(basename "$argusfile");
            echo "Writing $argusfile to csv";
            ra -nn -s stime,flgs,state,dur,proto,saddr,smac,sport,dir,daddr,dmac,dport,runtime,mean,sum,min,max,stos,dtos,pkts,spkts,dpkts,sttl,dttl,appbytes,bytes,sbytes,sappbytes,dbytes,dappbytes,load,sload,dload,loss,sloss,dloss,psloss,pdloss,rate,sintpkt,sintpktact,sintpktidl,dintpkt,dintpktact,dintp,ktidl,sjit,djit,smeansz,dmeansz,smaxsz,dmaxsz,sminsz,dminsz,label -c ',' -r "$argusfile" > flows/argus/"${filename%.*}"-argus.csv;
        done
        ;;

    "readtran")
        echo "Creating tranalyzer output for each caputre file";
        for capfile in caps/*.pcapng; do
            filename=$(basename "$capfile");
            echo "Generating tranalyzer output for $filename from pcap $capfile";
            tranalyzer -r $capfile -w flows/tran/"${filename%.*}"/.;
        done
        ;;

    "genalerts")
        ruleset="$2"
        echo "[Snort] Running all pcaps through snort, producing alert logs in logs/ directory";
        # Community Rules directory -  /opt/snort/etc/snort/rules/snort3-community.rules 
        for capfile in caps/*.pcapng; do
            filename=$(basename "$capfile");
            echo "[Snort] Running capture $filename through ruleset $ruleset";
            sudo snort -c /opt/snort/etc/snort/snort.lua -R rules/"$ruleset".rules --plugin-path /opt/snort/lib -r caps/"${filename%.*}".pcapng -A csv -y -q > ids-logs/"$ruleset"/"${filename%.*}"-alerts.csv
        done
        ;;
    *)
        echo "Usage: ./run.sh genargus";
        echo "Usage: ./run.sh readargus";
        echo "Usage: ./run.sh genalerts [RULESET_NAME]";;
esac

#ra -r ack-mirai.argus 
#ra -nn -s stime,flgs,state,dur,proto,saddr,smac,sport,dir,daddr,dmac,dport,runtime,mean,sum,min,max,stos,dtos,pkts,spkts,dpkts,sttl,dttl,appbytes,bytes,sbytes,sappbytes,dbytes,dappbytes,load,sload,dload,loss,sloss,dloss,psloss,pdloss,rate,sintpkt,sintpktact,sintpktidl,dintpkt,dintpktact,dintpktidl,sjit,djit,smeansz,dmeansz,smaxsz,dmaxsz,sminsz,dminsz,label -c','-r ARGUS_FILE > FLOW_FILE.csv

# tranalyzer -r caps/udp-mirai.pcapng -w tran/out/.
# editcap -A "2017-12-10 18:18:30.493113322" -B "2017-12-10 18:18:40.493113322" mirai-caps-original/caps/vse.pcapng mirai/caps/vse.pcapng
