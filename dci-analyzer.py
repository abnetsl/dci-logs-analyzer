from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

filename = input("Enter the DCI Logs filename: ")

destinationRequests = {}

with open(filename, 'r') as f:
    for line in f:
        if '/.TUDR' in line:
            messageStart = line.index('/.TUDR')
            trackingIdStart = messageStart + 28
            trackingIdLength = 14
            trackingIdEnd = trackingIdStart + trackingIdLength
            trackingId = line[trackingIdStart:trackingIdEnd]
            reqTime = datetime.strptime(line[0:12], '%H:%M:%S.%f')
            destinationRequests[trackingId] = { 'reqTime': reqTime, 'resTime': None, 'delay': None }
        if '/.TUMI' in line:
            messageStart = line.index('/.TUMI')
            trackingIdStart = messageStart + 28
            trackingIdLength = 14
            trackingIdEnd = trackingIdStart + trackingIdLength
            trackingId = line[trackingIdStart:trackingIdEnd]
            if trackingId not in destinationRequests:
                print("Warning: Response without request. Tracking ID: " + trackingId)
                continue
            resTime = datetime.strptime(line[0:12], '%H:%M:%S.%f')
            delay = resTime - destinationRequests[trackingId]['reqTime']
            delayMs = delay.seconds * 1000 + delay.microseconds / 1000
            if delayMs > 1000:
                print("Warning: Response time greater than 1 second. Tracking ID: " + trackingId)
            destinationRequests[trackingId]['resTime'] = resTime
            destinationRequests[trackingId]['delay'] =  delayMs

totalProcessTime = 0
totalRequests = 0
missingResponses = 0
totalValidResponseTimes = 0
maxResponseTime = 0
overOneSecond = 0
validResponseTimes = []

for key in destinationRequests:
    totalRequests += 1
    reqTime = destinationRequests[key]['reqTime']
    formattedTime = datetime.strftime(reqTime, '%H:%M:%S.%f')
    if destinationRequests[key]['resTime'] is not None:
        delay = destinationRequests[key]['delay']
        if delay > 1000:
            overOneSecond += 1
        if delay > maxResponseTime:
            print("Tracking ID: " + key)
            print("Request Time: " + formattedTime)
            maxResponseTime = delay
        if delay > 0:
            validResponseTimes.append(delay)
            totalProcessTime += delay
        resTime = destinationRequests[key]['resTime']
        formattedTime = datetime.strftime(resTime, '%H:%M:%S.%f')
    else:
        missingResponses += 1
        print("Response Time: N/A")
    print("")

print("Total Requests: " + str(totalRequests))
print("Average Process Time: " + str(totalProcessTime/(len(validResponseTimes))) + "ms")
print("Missing Responses: " + str(missingResponses))
print("Max Response Time: " + str(maxResponseTime) + "ms")
print("Responses over 1 second: " + str(overOneSecond))

# Generate a histogram of the response times
responseTimes = []
for key in destinationRequests:
    if destinationRequests[key]['resTime'] is not None and destinationRequests[key]['delay'] > 0:
        responseTimes.append(destinationRequests[key]['delay'])


medianResponseTime = np.median(responseTimes)
print("Median Response Time: " + str(medianResponseTime) + "ms")

for i in range(0, 101, 10):
    percentile = np.percentile(responseTimes, i)
    print("P(" + str(i) + ") Response Time: " + str(percentile) + "ms")

# Create a figure with two subplots

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Plot the histogram
ax1.hist(responseTimes, bins=min(50, len(responseTimes)), edgecolor='black')
ax1.set_title('Histogram of Response Times')
ax1.set_xlabel('Response Time (ms)')
ax1.set_ylabel('Frequency')
ax1.grid(True)

# Generate a scatter plot of the response times by request time
x = []
y = []

for key in destinationRequests:
    if destinationRequests[key]['reqTime'] is not None and destinationRequests[key]['delay'] is not None:
        x.append(datetime.strftime(destinationRequests[key]['reqTime'], '%H:%M:%S.%f'))
        y.append(destinationRequests[key]['delay'])

# Plot the scatter plot
ax2.scatter(x, y, s=1)
ax2.set_title('Response Time by Request Time')
ax2.set_xlabel('Request Time')
ax2.set_ylabel('Response Time (ms)')
# Reduce the number of x-axis labels
ax2.xaxis.set_major_locator(MaxNLocator(nbins=10))

# Adjust layout and show the plot
plt.tight_layout()
plt.show()
