<?php
function graph_slurm_sdiag_main_cycles_per_minute ( &$rrdtool_graph ) {
	global $rrd_dir;

	$series =
		  "DEF:'cycles'='${rrd_dir}/slurmmond_sdiag_main_cycles_per_minute.rrd':'sum':AVERAGE "
		. "LINE2:'cycles'#000000:'cycles/min' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Main Sche Cycle Rate --';
	$rrdtool_graph['vertical-label'] = 'cycles/min';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
