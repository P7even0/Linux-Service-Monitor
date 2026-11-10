# Linux Service Monitor

A lightweight Linux system monitoring utility built with **Python**, providing real-time information about system resource usage and HTTP service availability.

The application reads system metrics directly from Linux kernel interfaces and uses Python's standard library to calculate CPU, memory, and disk utilization. It also performs HTTP health checks to determine whether a monitored service is responding successfully.

This project was developed as a practical exercise in Linux system monitoring, operating system interfaces, and basic infrastructure observability.

## Features

- **CPU monitoring:** Calculates CPU utilization by comparing CPU time counters from `/proc/stat` across two measurements.
- **Memory monitoring:** Estimates RAM usage using information from `/proc/meminfo`.
- **Disk monitoring:** Reports filesystem utilization using Python's `shutil` module.
- **HTTP health checks:** Sends HTTP requests to a configured service and evaluates its response status.
- **Live terminal dashboard:** Continuously displays updated system metrics and service status.
- **Graceful shutdown:** Supports exiting the monitoring loop using `Ctrl+C`.

## Technologies Used

- Python 3
- Linux `/proc` filesystem
- Python Standard Library:
  - `time`
  - `os`
  - `shutil`
  - `http.client`

No external Python packages are required.

## How It Works

The monitor periodically collects system information, calculates resource utilization, checks the availability of an HTTP service, and displays the results in the terminal.

### CPU Monitoring

CPU utilization is calculated using accumulated CPU time counters provided by `/proc/stat`.

The program:

1. Reads the aggregate CPU counters.
2. Separates idle time from non-idle time.
3. Waits one second.
4. Reads the counters again.
5. Calculates CPU utilization using the differences between the two measurements.

For this implementation, idle time includes both the `idle` and `iowait` counters.

The monitor uses the first eight numeric CPU counters, avoiding double-counting the `guest` and `guest_nice` fields.

### Memory Monitoring

Memory information is retrieved from `/proc/meminfo`.

The program extracts:

- `MemTotal`: Total usable physical memory.
- `MemAvailable`: Estimated memory available for applications without swapping.

Memory utilization is calculated as:

\[
\text{RAM Usage} = \frac{\text{MemTotal}-\text{MemAvailable}}{\text{MemTotal}}\times100
\]

Using `MemAvailable` instead of `MemFree` accounts for memory that Linux can reclaim from caches and buffers.

### Disk Monitoring

Filesystem information is retrieved using:

```python
shutil.disk_usage("/")
```

The function provides the filesystem's total, used, and available space.

Disk utilization is calculated as:

\[
\text{Disk Usage} = \frac{\text{Used}}{\text{Used}+\text{Free}}\times100
\]

This measures the percentage of ordinarily available filesystem space that has been consumed, following the convention used by the Linux `df` utility.

The monitor checks the Linux root filesystem (`/`).

### HTTP Health Checks

The application uses Python's `http.client` module to send HTTP GET requests to a configured service.

The service is classified into three possible states:

| Status | Description |
|---|---|
| `ONLINE` | The server responds with an HTTP status code between 200 and 299. |
| `UNHEALTHY` | The server responds with an HTTP status outside the 200–299 range. |
| `OFFLINE` | The connection fails, times out, or encounters a supported HTTP communication error. |

By default, the monitor checks:

```text
http://localhost:8080/
```

The connection uses a two-second timeout to avoid waiting indefinitely for an unresponsive service.

A successful TCP connection alone does not guarantee that the HTTP service is functioning correctly, so the monitor also evaluates the HTTP response status.

### Continuous Monitoring

The program runs inside a continuous loop that:

1. Clears the terminal.
2. Collects CPU, memory, and disk metrics.
3. Performs an HTTP service health check.
4. Displays the results.
5. Waits before refreshing.

The CPU measurement includes a one-second sampling interval, and the main loop includes an additional two-second delay.

As a result, actual dashboard refresh intervals are approximately three seconds or longer, depending on HTTP response times and execution overhead.

## Requirements

- Python 3
- Linux environment
- Access to `/proc/stat` and `/proc/meminfo`

The application was developed and tested using **Ubuntu under Windows Subsystem for Linux (WSL)**.

It is designed for Linux systems and is not intended to run directly on Windows without a Linux environment.

## How to Run

### 1. Clone the Repository

```bash
git clone <repository-url>
cd linux-service-monitor
```

Replace `<repository-url>` with the repository's actual URL.

### 2. Run the Monitor

```bash
python3 monitor.py
```

The application starts displaying system metrics and checking the configured HTTP service.

### 3. Test HTTP Service Monitoring

To create a temporary local HTTP server, open another terminal and run:

```bash
python3 -m http.server 8080
```

The monitor should report:

```text
Service:         localhost:8080
Status:          ONLINE
```

Stop the HTTP server using `Ctrl+C`.

On the next successful refresh, the monitor should report:

```text
Service:         localhost:8080
Status:          OFFLINE
```

### 4. Stop the Monitor

Press `Ctrl+C` to terminate the monitoring loop.

The program exits gracefully and displays a shutdown message.

## Example Output

```text
========== LINUX SERVICE MONITOR ==========


Memory usage: 3.96%
CPU usage: 1.25%
Disk usage: 0.13%


Service:         localhost:8080
Status:          ONLINE

===========================================
```

*The values above are illustrative. Actual results depend on the system and its current workload.*

## Testing and Verification

The monitor was tested manually in an Ubuntu environment running under WSL.

### Memory Monitoring

Memory utilization was compared against the output of:

```bash
free -h
```

The calculated RAM usage was consistent with the system's reported memory statistics.

### CPU Monitoring

CPU monitoring was tested under both idle and active conditions.

CPU activity was generated using:

```bash
yes > /dev/null
```

Observed results included:

| Test Condition | Observed CPU Usage |
|---|---:|
| Idle system | Approximately 0% |
| CPU workload running | Approximately 15.93% |
| After stopping workload | Approximately 0% |

The monitor detected an increase in CPU utilization during the workload and a decrease after it stopped.

Because CPU utilization is measured across all available CPU cores, a workload occupying one core does not necessarily produce 100% overall CPU usage.

### Disk Monitoring

Disk utilization was compared against:

```bash
df -h /
```

The monitor reported approximately **0.13%** disk utilization, consistent with the filesystem's reported used and available space.

### HTTP Service Monitoring

The HTTP checker was tested using a temporary local HTTP server.

The monitor successfully detected the service's availability while running and its unavailability after the server was stopped.

### Testing Limitations

Testing was performed manually rather than through an automated test suite.

The results demonstrate expected behavior under the tested conditions but do not establish long-term reliability or performance under sustained workloads.

## Current Limitations

- **Linux-specific:** Depends on Linux kernel interfaces such as `/proc/stat` and `/proc/meminfo`.
- **Aggregate CPU monitoring:** Reports total CPU utilization rather than individual core usage.
- **Polling-based monitoring:** Collects metrics periodically rather than using event-driven monitoring.
- **Single filesystem:** Monitors only the root filesystem (`/`).
- **Single HTTP service:** Checks one configured HTTP endpoint.
- **Terminal-only interface:** Displays information locally without a graphical interface or remote dashboard.
- **No historical storage:** Metrics are displayed but not persisted for later analysis.
- **Basic health classification:** Uses HTTP response status codes rather than application-specific health criteria.
