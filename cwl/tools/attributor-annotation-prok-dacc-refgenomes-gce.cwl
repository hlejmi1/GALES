#!/usr/bin/env cwl-runner

cwlVersion: "cwl:draft-3"

class: CommandLineTool
baseCommand: attributor

requirements:
  - class: InlineJavascriptRequirement
  - class: CreateFileRequirement
    fileDef:
      - filename: attributor.config
        fileContent: |
            general:
               default_product_name: hypothetical protein
               allow_attributes_from_multiple_sources: No
               debugging_polypeptide_limit: 0
            indexes:
               coding_hmm_lib: $(inputs.hmm_attribute_lookup_file.path)
               uniref100: $(inputs.blast_attribute_lookup_file.path)
            input:
               polypeptide_fasta: $(inputs.polypeptide_fasta.path)
               gff3: $(inputs.source_gff3.path)
            order:
               - coding_hmm_lib__equivalog
               - rapsearch2__uniref100__trusted_full_full
               - coding_hmm_lib__equivalog_domain
               - rapsearch2__uniref100__trusted_partial_full
               - coding_hmm_lib__subfamily
               - coding_hmm_lib__superfamily
               - coding_hmm_lib__subfamily_domain
               - coding_hmm_lib__domain
               - coding_hmm_lib__pfam
               - rapsearch2__uniref100__trusted_full_partial
               - tmhmm
               #- lipoprotein_motif
               - coding_hmm_lib__hypothetical_equivalog
            evidence:
               - label: coding_hmm_lib__equivalog
                 type: HMMer3_htab
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.hmm_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.hmm_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: equivalog
                 index: coding_hmm_lib

               - label: coding_hmm_lib__equivalog_domain
                 type: HMMer3_htab
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.hmm_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.hmm_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: equivalog_domain
                 index: coding_hmm_lib

               - label: coding_hmm_lib__subfamily
                 type: HMMer3_htab
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.hmm_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.hmm_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: subfamily
                 index: coding_hmm_lib
                 append_text: family protein

               - label: coding_hmm_lib__superfamily
                 type: HMMer3_htab
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.hmm_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.hmm_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: superfamily
                 index: coding_hmm_lib
                 append_text: family protein

               - label: coding_hmm_lib__subfamily_domain
                 type: HMMer3_htab
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.hmm_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.hmm_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: subfamily_domain
                 index: coding_hmm_lib
                 append_text: domain protein

               - label: coding_hmm_lib__domain
                 type: HMMer3_htab
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.hmm_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.hmm_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: domain
                 index: coding_hmm_lib
                 append_text: domain protein

               - label: coding_hmm_lib__pfam
                 type: HMMer3_htab
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.hmm_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.hmm_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: pfam
                 index: coding_hmm_lib
                 append_text: family protein

               - label: coding_hmm_lib__hypothetical_equivalog
                 type: HMMer3_htab
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.hmm_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.hmm_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: hypoth_equivalog
                 index: coding_hmm_lib

               - label: rapsearch2__uniref100__trusted_full_full
                 type: RAPSearch2_m8
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.m8_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.m8_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: trusted
                 index: uniref100
                 query_cov: 80%
                 match_cov: 80%
                 percent_identity_cutoff: 50%

               - label: rapsearch2__uniref100__trusted_partial_full
                 type: RAPSearch2_m8
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.m8_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.m8_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: trusted
                 index: uniref100
                 match_cov: 80%
                 percent_identity_cutoff: 50%
                 append_text: domain protein

               - label: rapsearch2__uniref100__trusted_full_partial
                 type: RAPSearch2_m8
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.m8_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.m8_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 class: trusted
                 index: uniref100
                 query_cov: 80%
                 percent_identity_cutoff: 50%
                 append_text: domain protein

               - label: rapsearch2__uniref100__all_full_full
                 type: RAPSearch2_m8
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.m8_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.m8_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 index: uniref100
                 query_cov: 80%
                 match_cov: 80%
                 percent_identity_cutoff: 50%
                 prepend_text: putative

               - label: rapsearch2__uniref100__all_partial_full
                 type: RAPSearch2_m8
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.m8_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.m8_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 index: uniref100
                 match_cov: 80%
                 percent_identity_cutoff: 50%
                 prepend_text: putative
                 append_text: domain protein

               - label: rapsearch2__uniref100__all_full_partial
                 type: RAPSearch2_m8
                 path: ${
                   var r = "";
                   for (var i = 0; i < inputs.m8_files.length; i++) {
                     if (i > 0) {
                       r += ",";
                     }
                     r += inputs.m8_files[i].path.replace('file://','');
                   }
                   return r;
                 }
                 index: uniref100
                 query_cov: 80%
                 percent_identity_cutoff: 50%
                 prepend_text: putative
                 append_text: domain protein

               - label: tmhmm
                 type: TMHMM
                 product_name: putative integral membrane protein
                 min_helical_spans: 5
                 path: ${
                  var r = "";
                  for (var i = 0; i < inputs.tmhmm_files.length; i++) {
                    if (i > 0) {
                    r += ",";
                   }
                    r += inputs.tmhmm_files[i].path.replace('file://','');
                  }
                  return r;
                }

hints:
  - class: DockerRequirement
    dockerPull: jorvis/gales-gce

inputs:
  - id: config_file
    type: string
    inputBinding:
      prefix: -c
      separate: true
      position: 1
  - id: output_base
    type: string
    inputBinding:
      position: 2
      prefix: -o
      separate: true
  - id: output_format
    type: string
    inputBinding:
      position: 3
      prefix: -f
      separate: true
  - id: hmm_attribute_lookup_file
    type: File
  - id: blast_attribute_lookup_file
    type: File
  - id: polypeptide_fasta
    type: File
  - id: source_gff3
    type: File
  - id: hmm_files
    type:
      type: array
      items: File
  - id: m8_files
    type:
      type: array
      items: File
  - id: tmhmm_files
    type:
      type: array
      items: File


outputs:
  - id: output_files
    type: 
      type: array
      items: File
    outputBinding:
      glob: $(inputs.output_base + '*')
