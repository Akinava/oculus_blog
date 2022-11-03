# HOWTO
python3 src/tagging.py Video
# copy video from 1.tagged for timing in to 2.timed
mv Video/1.tagged/*_Lis.mp4 Video/2.timed/
mv Video/1.tagged/*_laser.mp4 Video/2.timed/
# create txt timing files
for x in $(ls Video/2.timed); do echo $x; touch "Video/2.timed/${x%.mp4}.txt"; done
# copy rest video files from 1.tagged in to 2.timed
# make timing
x=./Video/2.timed/123456. ; gedit ${x}txt& mplayer ${x}mp
# cat video
python3 src/cutter.py Video
# upload from 3.to_post to youtube
python3 src/studio.py Video
### done

# TODO
fix artifacts
