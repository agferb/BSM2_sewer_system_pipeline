#!/usr/bin/env nextflow

// Import the star indexing and alignment processes from the modules
// ...


params {
    // General parameters
    datadir: Path = "${launchDir}/data1"
    outdir: String = "${launchDir}/results"

    // Input parameters
    samplesheet: Path = "${launchDir}/samplesheet_project.csv"
    
    // fastp
    qualified_quality_phred: Integer = 28
    cut_tail: Boolean = true
    length_required: Integer = 30
    n_base_limit: Integer =  0
    FW_PRIMER: String = "GTGCCAGCAGCCGCGGTAA"
    RV_PRIMER: String = "GGACTACACGGGTTTCTAAT"

}

include { fastqc as fastqc_raw; fastqc as fastqc_trim } from "./modules/fastqc" //addParams(OUTPUT: fastqcOutputFolder)
include { fastp } from "./modules/fastp"
include { multiqc as multiqc_raw; multiqc as multiqc_trim } from "./modules/multiqc"
include { dada2 } from "./modules/dada2"

// Running a workflow with the defined processes here.  
workflow {
    log.info """\
        LIST OF PARAMETERS
    ================================
                GENERAL
    Data-folder      : ${params.datadir}
    Results-folder   : ${params.outdir}
    ================================
        INPUT & REFERENCES 
    Samplesheet      : ${params.samplesheet}
    ================================
                FASTP
    qualified_quality_phred : ${params.qualified_quality_phred}
    cut_tail                : ${params.cut_tail}
    length_required         : ${params.length_required}
    n_base_limit            : ${params.n_base_limit}
    adapter_sequence        : ${params.FW_PRIMER}
    adapter_sequence_r2     : ${params.RV_PRIMER}
    """
    // Also channels are being created. 
    def read_pairs_ch = channel.fromPath( params.samplesheet, checkIfExists: true )
        .splitCsv(header:true)
        .map{ row -> tuple( row.sample, [file(row.fastq_1, checkIfExists: true), file(row.fastq_2, checkIfExists: true)] ) }

    // QC on raw reads
    fastqc_raw(read_pairs_ch)

    // Multi QC on results
    multiqc_raw(fastqc_raw.out.fastqc_out.collect())
        
    // Fastp on QC results
    fastp(read_pairs_ch,
        params.qualified_quality_phred,
        params.cut_tail,
        params.length_required,
        params.n_base_limit,
        params.FW_PRIMER,
        params.RV_PRIMER
    )

    // Fast and multi QC on trimmed results
    fastqc_trim(fastp.out.trim_FW_fq)
    multiqc_trim(fastqc_trim.out.fastqc_out.collect())

    // dada2 to generate plots
    def dada2_input = fastp.out.trim_FW_fq.mix(fastp.out.trim_RV_fq)
        .map{_sample, reads -> reads} // '_' is to ignore parameter
        .collect()
    dada2(dada2_input)

    workflow.onComplete = {
        println "Pipeline completed at: ${workflow.complete}"
        println "Time to complete workflow execution: ${workflow.duration}"
        println "Execution status: ${workflow.success ? 'Succesful' : 'Failed' }"
    }

    workflow.onError = {
        println "Oops... Pipeline execution stopped with the following message: ${workflow.errorMessage}"
    }
    
}