## Compiles the JMP into a pdf using `codebraid`

PARAMS=(
pandoc 
-f markdown+raw_tex
-t latex 
--include-in-header=template.tex 
--overwrite
# --filter pandoc-xnos
-o report.tex
report.cbmd
)

codebraid ${PARAMS[@]}


# Now second time around

PANDOC_PARAMS=(
-o report.docx
report.tex
)

pandoc ${PANDOC_PARAMS[@]}