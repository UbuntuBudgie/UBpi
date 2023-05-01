#!/usr/bin/env bash

CODENAME="lunar"
BASEIMAGE="$CODENAME-preinstalled-desktop-arm64+raspi.img"
IMAGE="PI-IMAGE.img"
RELEASE="cdimage.ubuntu.com/daily-preinstalled/current"
RELEASEIMAGE="$CODENAME-budgie-preinstalled-desktop-arm64+raspi.img"
SHA256SUMS="SHA256SUMS"
MOUNT="/mnt/pi"
NAMESERVER=1.1.1.1

# check if we have persmissions, and the correct packages are installed
if [ "$(id -u)" -ne 0 ]; then
  echo "You need to be root to run this."
  exit 1
fi

if [ ! -f "/usr/bin/qemu-arm-static" ]; then
  echo "Please make sure to install the following packages:"
  echo "   binfmt-support"
  echo "   qemu-user-static"
  exit 1
fi

# Start in the script directory (and remember it for later)
cd ${0%/*}
SCRIPT_PATH=$(pwd)
echo $SCRIPT_PATH

# If we have a successfully built image, instead of overwriting it,
# back it up by prepending a timestamp
if test -f "$RELEASEIMAGE.xz"; then
    PREFIX=$(date -r budgie-image.sh "+%m-%d-%Y-%H:%M:%S")
    echo "$RELEASEIMAGE.xz exists... backing up"
    mv $RELEASEIMAGE.xz ${PREFIX}_${RELEASEIMAGE}.xz
fi

# Download the latest image
zsync http://${RELEASE}/${BASEIMAGE}.xz.zsync

# Let's grab the SHA256SUM and double check the base image is ok
# before we distribute an image based on it
wget https://${RELEASE}/${SHA256SUMS} -O $SHA256SUMS
echo "Verifying Image"
if sha256sum -c $SHA256SUMS 2>&1 | grep OK; then
    echo "Image successfully verified"
else
    echo "Could not verify image. Bad SHA256SUM match"
    exit
fi

# Delete any possible incomplete temp image and copy the image to a temp
# so we don't modify the original and defeat the purpose of zsync
if [ -f "$IMAGE.xz" ]; then
    rm $IMAGE.xz
    echo "Removing existing $IMAGE.xz"
fi
if [ -f "$IMAGE" ]; then
    rm $IMAGE
    echo "Removing existing $IMAGE"
fi
cp $BASEIMAGE.xz $IMAGE.xz

echo "Uncompressing image"
xz -d -v $IMAGE.xz

# Set up the chroot environment
echo "Creating mount"
OFFSET=$(parted "$IMAGE" unit b print | grep "ext4" | awk '{ print substr($2,0,length($2)-1) }')
mkdir -p $MOUNT
mount -o loop,offset=$OFFSET $IMAGE $MOUNT
cp seed.yaml $MOUNT/var/lib/snapd/seed/seed.yaml
cp /usr/bin/qemu-arm-static $MOUNT/usr/bin/
cp setup-budgie.dontrun $MOUNT/usr/bin/setup-budgie.sh

# If we want to install any .debs, we can place them in the patches folder
# They will automatically be installed by the conversion script
cp patches/*.deb $MOUNT/tmp

chmod +x $MOUNT/usr/bin/setup-budgie.sh
rm $MOUNT/run/systemd/resolve/stub-resolv.conf
echo "nameserver $NAMESERVER" > tempconf.tmp
cp tempconf.tmp $MOUNT/run/systemd/resolve/stub-resolv.conf
rm tempconf.tmp
cd $MOUNT
mount -t proc /proc proc/
mount --rbind /sys sys/
mount --rbind /dev dev/

# Create the image
echo "Running conversion"
chroot $MOUNT /usr/bin/setup-budgie.sh

# Clean up the image
rm $MOUNT/usr/bin/qemu-arm-static
rm $MOUNT/tmp/*.deb

# Clean up local machine. Regardless, local machine will be in an unstable state after this
# and should ultimately be reboot on completion
sleep 10
umount $MOUNT/proc
umount -l $MOUNT/sys
umount -l $MOUNT/dev
sleep 10
umount $MOUNT
rmdir $MOUNT

echo "changing to $SCRIPT_PATH"
cd $SCRIPT_PATH

# Rename the temp image now that it is complete
mv $IMAGE $RELEASEIMAGE

# Next line will take a long time to recompress unless you are using a 16 core NVME based Ryzen 7 or better machine!
xz -v -9 --threads=0 $RELEASEIMAGE

chown ${SUDO_USER}:${SUDO_USER} * &>/dev/null

echo "Build complete. Please reboot."
