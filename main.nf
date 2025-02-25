#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

// Initialise pipeline's input parameters
params.seqfile = null
params.structdir = null // Directory containing structure files
params.simfile = null
params.idfile = null
params.k = null
params.solver = 0
params.measure = 0
params.mat = null // Path to existing mat.npy
params.head = null // Path to existing headings.json

// Create timestamped output directory
def timestamp = new java.util.Date().format('yyyy-MM-dd_HH-mm-ss')
params.outdir = "results_${timestamp}"

// Create output directory
outdir = file(params.outdir)
outdir.mkdirs()

k = params.k
solver = params.solver
measure = params.measure

// Input validation
def inputCount = [params.mat && params.head, params.simfile, params.seqfile, params.structdir].count { it }

if (inputCount == 0) {
    error """
    ERROR: No input provided!
    Please provide ONE of the following:
    1. Existing matrix and heading files (--mat and --head)
    2. Sequence FASTA file (--seqfile)
    3. Structure directory (--structdir)
    4. Similarity file (--simfile)
    """
}

// If sequence fasta is provided
seq_ch = params.seqfile ? Channel.fromPath(params.seqfile, checkIfExists: true) : Channel.empty()
// If structure directory is provided
struct_ch = params.structdir ? Channel.fromPath(params.structdir, checkIfExists: true) : Channel.empty()
// If similarity txt file is provided
sim_ch = params.simfile ? Channel.fromPath(params.simfile, checkIfExists: true) : Channel.empty()
// If solution txt file is provided
sol_ch = params.idfile ? Channel.fromPath(params.idfile, checkIfExists: true) : Channel.empty()

// If matrix and headings files exit, use them directly
if (params.mat && params.head) {
    mat_ch = Channel.fromPath(params.mat, checkIfExists: true)
    head_ch = Channel.fromPath(params.head, checkIfExists: true)
}


// Process 1a: run needleall.py for sequence similarities
process runNeeleall{

    publishDir outdir, mode: 'copy'

    input:
    path fasta

    output:
    path "identities.txt", emit: identities
    path "similarities.txt", emit: similarities

    when:
    params.seqfile

    script:
    """
    python3 ${workflow.projectDir}/create_matrix/needleall.py $fasta
    """
}

// Process 1b: run foldseek.py for structure similarities
process runFoldseek{

    publishDir outdir, mode: 'copy'

    input:
    path structs

    output:
    path "tmscores.txt", emit: tmscores

    when:
    params.structdir

    script:
    """
    python3 ${workflow.projectDir}/create_matrix/foldseek.py $structs
    """
}

// Process 2: initialise matrix and headings
process initMatrix{

    publishDir outdir, mode: 'copy'

    input:
    path input

    output:
    path "*.npy", emit: mat
    path "*.json", emit: head

    when:
    params.seqfile || params.structdir || params.simfile

    script:
    """
    python3 ${workflow.projectDir}/init_head_mat.py $input $measure
    """
}

// Process 3: run the main diversity problem script
process solveMDP{

    publishDir outdir, mode: 'copy'

    input:
    path mat
    path head

    output:
    path "*.txt", emit: subset
    path "*.pdf", optional: true, emit: plot

    script:
    """
    python3 ${workflow.projectDir}/main.py -hd $head -d $mat -k $k -s $solver -m $measure
    """
}

// Process 4: run the solution expand script
process expandMDP{

    publishDir outdir, mode: 'copy'

    input:
    path mat
    path head
    path sol

    output:
    path "*.txt", emit: subset
    path "*.pdf", optional: true, emit: plot

    when:
    params.idfile

    script:
    """
    python3 ${workflow.projectDir}/main.py -hd $head -d $mat -e $sol -k $k -s $solver -m $measure
    """
}


workflow {
    if (params.seqfile) {
        runNeeleall(seq_ch)

        def matrixInput
        if (params.measure == 1) {
            matrixInput = runNeeleall.out.identities
        } else if (params.measure == 2) {
            matrixInput = runNeeleall.out.similarities
        } else if (params.measure == 0 || !params.measure) {
            // If mode 0 or no specific measure is used
            matrixInput = channel.fromList([runNeeleall.out.identities, runNeeleall.out.similarities])
        }
        initMatrix(matrixInput)
        solveMDP(initMatrix.out.mat, initMatrix.out.head) 
        
    } else if (params.structdir) {
        runFoldseek(struct_ch)
        initMatrix(runFoldseek.out.tmscores)
        solveMDP(initMatrix.out.mat, initMatrix.out.head)
    } else if (params.simfile) {
        initMatrix(sim_ch)
        solveMDP(initMatrix.out.mat, initMatrix.out.head)
    } else if (params.mat && params.head) {
        solveMDP(mat_ch, head_ch)
    } else if (params.mat && params.head && params.idfile) {
        expandMDP(mat_ch, head_ch, sol_ch)
    }
}

workflow.onComplete {
    println """\
    Pipeline execution summary
    --------------------------
    Completed at: ${workflow.complete}
    Duration    : ${workflow.duration}
    Success     : ${workflow.success}
    Work dir    : ${workflow.workDir}
    Output dir  : ${params.outdir}
    Error report: ${workflow.errorReport}
    """.stripIndent()
}
