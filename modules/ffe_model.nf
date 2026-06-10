process ffe_model {
  publishDir {"${params.outdir}/${sub_areas}_subareas/"}, mode: 'copy', overwrite: true
  label 'low'
  container 'docker://aleitocu/bsm2_ffe_model:01.00'
  
  input:
  path(input_data)
  path(flow_data)
  tuple val(sub_areas), val(t_min), val(t_max)

  output:
  path("solids_after_${sub_areas}_subareas_${t_min}_${t_max}.csv"), emit: solids_data
  path("solids_after_${sub_areas}_subareas_${t_min}_${t_max}.png"), emit: solids_plot

  script:
  """
  ${input_data} ${flow_data} --t_min ${t_min} --t_max ${t_max}
  """
}

