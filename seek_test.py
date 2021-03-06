import sys, os, time, random


#--------------------------------------------------------------------------------------------------

def BytesString(n):
    suffixes = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    suffix = 0
    while n % 1024 == 0 and suffix+1 < len(suffixes):
        suffix += 1
        n /= 1024
    return '{0}{1}'.format(n, suffixes[suffix])

def BytesInt(s):
    if all(c in '0123456789' for c in s):
        return int(s)
    suffixes = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    for power,suffix in reversed(list(enumerate(suffixes))):
        if s.endswith(suffix):
            return int(s.rstrip(suffix))*1024**power
    raise ValueError('BytesInt requires proper suffix ('+' '.join(suffixes)+').')

def BytesStringFloat(n):
    x = float(n)
    suffixes = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    suffix = 0
    while x > 1024.0 and suffix+1 < len(suffixes):
        suffix += 1
        x /= 1024.0
    return '{0:0.2f}{1}'.format(x, suffixes[suffix])


#--------------------------------------------------------------------------------------------------

disk = open('/dev/sda', 'r')
disk.seek(0,2)
disksize = disk.tell()
os.system('echo noop | sudo tee /sys/block/sda/queue/scheduler > /dev/null')

print 'Syntax: progam [-s -sr -t -tr] [-v]:  to run specific modes; for verbose mode.'
print 'Disk name: {0}  Disk size: {1}  Scheduler disabled.'.format(
    disk.name, BytesStringFloat(disksize))

displaytimes = '-v' in sys.argv


#--------------------------------------------------------------------------------------------------

bufsize = 512
bufcount = 100
displaysamplecount = 24

for randomareas in [False,True]:
    print
    print 'Measuring: Random seek time {0}'.format(
        'using random areas of disk.' if randomareas else 'using beginning of disk.')
    print 'Samples: {0}{1}   Sample size: {2}'.format(
        bufcount, ' (displayed {0})'.format(displaysamplecount) if displaytimes else '', bufsize)

    for area in [BytesInt('50KB')*2**i for i in range(0,64)]+[disksize]:
        if area > disksize:
            continue

        os.system('echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null')

        times = []
        disk.seek(0)
        disk.read(bufsize)
        for _ in range(bufcount):
            left = random.randint(0, disksize-area) if randomareas else 0
            right = left + random.randint(0, area)
            disk.seek(left)
            disk.read(bufsize)
            start = time.time()
            disk.seek(right)
            disk.read(bufsize)
            finish = time.time()
            times.append(finish-start)

        times = sorted(times)[:bufcount*95/100]
        print 'Area tested: {0:6}   Average: {1:5.2f} ms   Max: {2:5.2f} ms   Total: {3:0.2f} sec'.format(
            BytesString(area) if area < disksize else BytesStringFloat(area), 
            sum(times)/len(times)*1000, max(times)*1000, sum(times))
        if displaytimes:
            print 'Read times: {0} ... {1} ms'.format(
                ' '.join(['{0:0.2f}'.format(x*1000) for x in times[:displaysamplecount/2]]), 
                ' '.join(['{0:0.2f}'.format(x*1000) for x in times[-displaysamplecount/2:]]))