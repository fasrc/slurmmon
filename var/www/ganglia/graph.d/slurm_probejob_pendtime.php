<?php


function graph_slurm_probejob_pendtime ( &$rrdtool_graph ) {
        global $rrd_dir;

        $config = file_get_contents("/etc/slurmmon.conf");
        $json_conf= json_decode($config,true);

        $series="";
        foreach ( $json_conf['probejob_partitions'] as $partition)
        {
                $series =  $series."DEF:'".$partition."'='${rrd_dir}/slurmmond_probejob_pendtime_".$partition.".rrd':'sum':AVERAGE ";
                                
        }

        $colours=array("#00000f","#FF0000","#00FF00","#FFFF00","#0000FF");
        $i=0;
        foreach ( $json_conf['probejob_partitions'] as $partition)
        {
                $series =  $series."LINE2:'".$partition."'".$colours[$i].":'".$partition."' ";
                $i++;
                                
        }

        
        //required
        $rrdtool_graph['title'] = '-- Slurm Time Probe Jobs Spent Pending --';
        $rrdtool_graph['vertical-label'] = 'seconds';
        $rrdtool_graph['series'] = $series;

        //      return $rrdtool_graph;
}
?>
