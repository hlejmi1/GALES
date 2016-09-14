#!/usr/bin/env cwl-runner

cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: rapsearch

# rapsearch -q query.fa -d nr -o output_file

requirements:
- class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: jorvis/falcon-gce

inputs:
  - id: database_file
    #  Not defined as a file because the base name is
    #  sufficient.
    type: string
    inputBinding:
      prefix: -d
      separate: true
      position: 1
  - id: query_file
    type: File
    inputBinding:
      position: 2
      prefix: -q
      separate: true
  - id: output_file_base
    type: string
    inputBinding:
      position: 3
      prefix: -o
      separate: true
  - id: thread_count
    type: int
    inputBinding:
      position: 4
      prefix: -z
      separate: true
outputs:
  - id: output_base
    type: File
    outputBinding:
      glob: $(inputs.output_file_base + '.m8')