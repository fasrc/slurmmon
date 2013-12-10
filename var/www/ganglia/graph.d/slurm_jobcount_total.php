<?php
function graph_slurm_jobcount_total ( &$rrdtool_graph ) {
	global $rrd_dir;
	
	$series =
		  "DEF:'running'='${rrd_dir}/slurmmond_jobcount_total_running.rrd':'sum':AVERAGE "
		. "DEF:'pending'='${rrd_dir}/slurmmond_jobcount_total_pending.rrd':'sum':AVERAGE "
		. "LINE2:'running'#0000ff:'running' "
		. "LINE2:'pending'#ff0000:'pending' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Total Jobs --';
	$rrdtool_graph['vertical-label'] = 'jobs';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
