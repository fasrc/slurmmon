<?php
function graph_slurm_probejob_pendtime ( &$rrdtool_graph ) {
	global $rrd_dir;
	
	$series =
		  "DEF:'general'='${rrd_dir}/slurmmond_probejob_pendtime_general.rrd':'sum':AVERAGE "
		. "DEF:'interact'='${rrd_dir}/slurmmond_probejob_pendtime_interact.rrd':'sum':AVERAGE "
		. "LINE2:'general'#0000ff:'general' "
		. "LINE2:'interact'#00ff00:'interact' "
		;
	
	//required
	$rrdtool_graph['title'] = '-- Slurm Time Probe Jobs Spent Pending --';
	$rrdtool_graph['vertical-label'] = 'seconds';
	$rrdtool_graph['series'] = $series;

	return $rrdtool_graph;
}
?>
