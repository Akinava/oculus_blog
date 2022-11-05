# HOWTO
python3 src/tagging.py Video
# copy video from 1.tagged for timing in to 2.timed
mv Video/1.tagged/*_paintball.mp4 Video/2.timed/
mv Video/1.tagged/*_laser.mp4 Video/2.timed/
# create txt timing files
for x in $(ls Video/2.timed); do echo $x; touch "Video/2.timed/${x%.mp4}.txt"; done
# copy rest video files from 1.tagged in to 2.timed
# make timing
for x in $(ls Video/2.timed/*.mp4); do gedit ${x%.mp4}.txt& mplayer ${x}; done
# cat video
python3 src/cutter.py Video
# upload from 3.to_post to youtube
python3 src/studio.py Video
### done

# TODO
fix video artifacts
