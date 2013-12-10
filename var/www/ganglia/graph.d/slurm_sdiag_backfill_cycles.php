<?php
function graph_slurm_sdiag_backfill_cycles ( &$rrdtool_graph ) {
	global $rrd_dir;

	$series =
		  "DEF:'cycles'='${rrd_dir}/slurmmond_sdiag_backfill_total_cycles.rrd':'sum':AVERAGE "
		. "LINE2:'cycles'#000000:'cycles' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Backfill Sched Cycles Since SDIAG Reset --';
	$rrdtool_graph['vertical-label'] = 'cycles';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
