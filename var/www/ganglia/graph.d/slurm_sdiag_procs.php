<?php
function graph_slurm_sdiag_procs ( &$rrdtool_graph ) {
	global $rrd_dir;
	
	$series =
		  "DEF:'threads'='${rrd_dir}/slurmmond_sdiag_server_thread_count.rrd':'sum':AVERAGE "
		. "DEF:'agents'='${rrd_dir}/slurmmond_sdiag_agent_queue_size.rrd':'sum':AVERAGE "
		. "LINE2:'threads'#0000ff:'sever thread count' "
		. "LINE2:'agents'#ff0000:'agent queue size' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Processes --';
	$rrdtool_graph['vertical-label'] = 'count';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
