<?php
function graph_slurm_sdiag_main_cycles ( &$rrdtool_graph ) {
	global $rrd_dir;

	$series =
		  "DEF:'cycles'='${rrd_dir}/slurmmond_sdiag_main_total_cycles.rrd':'sum':AVERAGE "
		. "LINE2:'cycles'#000000:'cycles' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Main Sched Cycles Since SDIAG Reset --';
	$rrdtool_graph['vertical-label'] = 'cycles';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
