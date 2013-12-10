<?php
function graph_slurm_sdiag_jobs ( &$rrdtool_graph ) {
	global $rrd_dir;
	
	$series =
		  "DEF:'submitted'='${rrd_dir}/slurmmond_sdiag_jobs_submitted.rrd':'sum':AVERAGE "
		. "DEF:'started'='${rrd_dir}/slurmmond_sdiag_jobs_started.rrd':'sum':AVERAGE "
		. "DEF:'canceled'='${rrd_dir}/slurmmond_sdiag_jobs_canceled.rrd':'sum':AVERAGE "
		. "DEF:'failed'='${rrd_dir}/slurmmond_sdiag_jobs_failed.rrd':'sum':AVERAGE "
		. "DEF:'completed'='${rrd_dir}/slurmmond_sdiag_jobs_completed.rrd':'sum':AVERAGE "
		. "LINE2:'submitted'#000000:'submitted' "
		. "LINE2:'started'#00ff00:'started' "
		. "AREA:'canceled'#ffff00:'canceled' "
		. "STACK:'failed'#ff0000:'failed' "
		. "STACK:'completed'#0000ff:'completed' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Jobs Since SDIAG Reset --';
	$rrdtool_graph['vertical-label'] = 'jobs';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
