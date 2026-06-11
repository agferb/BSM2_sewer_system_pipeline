#!/usr/bin/env nextflow

// Import the star indexing and alignment processes from the modules
// ...


params {
    outdir = "${launchDir}/data"
    sub_areas  = [2, 4, 8]
    t_interval = [[0, 40], [360, 380]]
}

include { get_data } from "./modules/get_data"
include { sewer_model } from "./modules/sewer_model"
include { ffe_model } from "./modules/ffe_model"

// Running a workflow with the defined processes here.  
workflow {
    log.info """\
        LIST OF PARAMETERS
    ================================
        GENERAL
    Results-folder   : ${params.outdir}
    ================================
        INPUT & REFERENCES 
    ================================
        MODELS
    numer of sub-areas  : ${params.sub_areas}
    analysis intervals  : ${params.t_interval}
    """

    // Get BSM2 data
    get_data()

    // Transform model parameters to correct format
    def sub_areas_ch = channel.from( params.sub_areas )

    def t_interval_ch = channel.from( params.t_interval )
        .filter{tup -> tup[0] >= 0}
        .filter{tup -> tup[1] <= 609}

    def parameters_ch = sub_areas_ch
        .combine(t_interval_ch)

    // Run sewer model
    sewer_model(get_data.out.full_data, parameters_ch)

    // Run first-flush model
    ffe_model(get_data.out.full_data, sewer_model.out.flow_data, parameters_ch)

    // End pipeline verbose
    workflow.onComplete = {
        println "Pipeline completed at: ${workflow.complete}"
        println "Time to complete workflow execution: ${workflow.duration}"
        println "Execution status: ${workflow.success ? 'Succesful' : 'Failed' }"
    }

    workflow.onError = {
        println "Oops... Pipeline execution stopped with the following message: ${workflow.errorMessage}"
    }
    
}