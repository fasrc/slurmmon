<?php
function graph_slurm_sdiag_backfill_depths ( &$rrdtool_graph ) {
	global $rrd_dir;

	$series =
		  "DEF:'dmtd'='${rrd_dir}/slurmmond_sdiag_backfill_depth_mean_try_depth.rrd':'sum':AVERAGE "
		. "DEF:'qlm'='${rrd_dir}/slurmmond_sdiag_backfill_queue_length_mean.rrd':'sum':AVERAGE "
		. "DEF:'ldcts'='${rrd_dir}/slurmmond_sdiag_backfill_last_depth_cycle_try_sched.rrd':'sum':AVERAGE "
		. "DEF:'ldc'='${rrd_dir}/slurmmond_sdiag_backfill_last_depth_cycle.rrd':'sum':AVERAGE "
		. "DEF:'lql'='${rrd_dir}/slurmmond_sdiag_backfill_last_queue_length.rrd':'sum':AVERAGE "
		. "DEF:'dm'='${rrd_dir}/slurmmond_sdiag_backfill_depth_mean.rrd':'sum':AVERAGE "
		//. "LINE2:'dmtd'#cccccc:'depth mean try depth' "
		//. "LINE2:'qlm'#666666:'queue length mean' "
		. "LINE2:'ldcts'#ffff00:'last try sched' "
		. "LINE2:'ldc'#00ff00:'last depth' "
		. "LINE2:'lql'#000000:'queue length' "
		. "LINE2:'dm'#0d98ba:'mean depth' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Backfill Sched Depths --';
	$rrdtool_graph['vertical-label'] = 'jobs';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
