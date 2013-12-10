<?php
function graph_slurm_sdiag_main_depths ( &$rrdtool_graph ) {
	global $rrd_dir;

	$series =
		  "DEF:'lql'='${rrd_dir}/slurmmond_sdiag_main_last_queue_length.rrd':'sum':AVERAGE "
		. "DEF:'mdc'='${rrd_dir}/slurmmond_sdiag_main_mean_depth_cycle.rrd':'sum':AVERAGE "
		. "LINE2:'lql'#000000:'queue length' "
		. "LINE2:'mdc'#0d98ba:'mean depth' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Main Sched Depths --';
	$rrdtool_graph['vertical-label'] = 'jobs';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
