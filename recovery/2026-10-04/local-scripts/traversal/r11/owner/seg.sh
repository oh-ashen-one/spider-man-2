M=/Users/midir/sm2-n1/_scratch/refs/owner/flips_owner_2026-09-29.mov
for seg in "8.3 3.2 s3" "21.3 2.6 s6" "0.8 1.8 s1" "4.6 1.6 s2" "14.8 1.0 s5"; do set -- $seg
rm -rf d_$3; mkdir d_$3
ffmpeg -v error -y -copyts -ss $1 -i $M -to $(echo "$1+$2" | bc) -vf "fps=25,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=26:fontcolor=yellow:box=1:boxcolor=black,scale=240:-1" d_$3/%03d.jpg
ffmpeg -v error -y -framerate 25 -i d_$3/%03d.jpg -vf tile=10x8 -frames:v 1 z25_$3.jpg
echo $3 $(ls d_$3 | wc -l); done
