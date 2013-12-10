<?php
function graph_slurm_sdiag_main_times ( &$rrdtool_graph ) {
	global $rrd_dir;

	$series =
		  "DEF:'max'='${rrd_dir}/slurmmond_sdiag_main_max_cycle.rrd':'sum':AVERAGE "
		. "DEF:'mean'='${rrd_dir}/slurmmond_sdiag_main_mean_cycle.rrd':'sum':AVERAGE "
		. "DEF:'last'='${rrd_dir}/slurmmond_sdiag_main_last_cycle.rrd':'sum':AVERAGE "
		. "LINE2:'max'#ff0000:'max cycle' "
		. "LINE2:'mean'#00ff00:'mean cycle' "
		. "LINE2:'last'#0000ff:'last cycle' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Main Sched Cycle Times --';
	$rrdtool_graph['vertical-label'] = 'microseconds';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
