<?php
function graph_slurm_jobcount_one_user ( &$rrdtool_graph ) {
	global $rrd_dir;
	
	$series =
		  "DEF:'running'='${rrd_dir}/slurmmond_jobcount_max_running_one_user.rrd':'sum':AVERAGE "
		. "DEF:'pending'='${rrd_dir}/slurmmond_jobcount_max_pending_one_user.rrd':'sum':AVERAGE "
		. "LINE2:'running'#0000ff:'running' "
		. "LINE2:'pending'#ff0000:'pending' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Max Jobs by a Single User --';
	$rrdtool_graph['vertical-label'] = 'jobs';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
