<?php
function graph_slurm_sdiag_backfill_jobs ( &$rrdtool_graph ) {
	global $rrd_dir;
	
	$series =
		  "DEF:'slurm'='${rrd_dir}/slurmmond_sdiag_backfill_total_backfilled_jobs_since_last_slurm_start.rrd':'sum':AVERAGE "
		. "DEF:'cycle'='${rrd_dir}/slurmmond_sdiag_backfill_total_backfilled_jobs_since_last_stats_cycle_start.rrd':'sum':AVERAGE "
		. "LINE2:'slurm'#0000ff:'since slurm start' "
		. "LINE2:'cycle'#0d98ba:'since stats cycle start' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Backfilled Jobs --';
	$rrdtool_graph['vertical-label'] = 'jobs';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
