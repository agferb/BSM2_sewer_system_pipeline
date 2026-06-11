process sewer_model {
  publishDir {"${params.outdir}/${sub_areas}_subareas/"}, mode: 'copy', overwrite: true
  containerOptions { "--bind ${task.workDir}:/data" }   // Apptainer syntax
  label 'low'
  container 'docker://aleitocu/bsm2_sewer_model:01.00'
  
  input:
  path(input_data)
  tuple val(sub_areas), val(t_min), val(t_max)

  output:
  path("flow_after_${sub_areas}_subareas_*.csv"), emit: flow_data
  path("flow_after_${sub_areas}_subareas_*.png"), emit: flow_plot

  script:
  """
  python /model_sewer.py ${input_data} --t_min ${t_min} --t_max ${t_max} --sub_areas ${sub_areas}
  """
}

