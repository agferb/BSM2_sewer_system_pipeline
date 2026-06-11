process get_data {
  label 'low'
  container 'docker://aleitocu/bsm2_get_data:02.00'

  output:
  path("bsm2_full_data.txt"), emit: full_data

  script:
  """
  /get_data.sh
  echo "Data imported succesfully."
  """
}

