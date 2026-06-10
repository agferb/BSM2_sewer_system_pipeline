process get_data {
  label 'low'
  container 'docker://aleitocu/bsm2_get_data:01.00'

  output:
  path("full_bsm2_data.txt"), emit: full_data

  script:
  """
  echo "Data imported succesfully."
  """
}

