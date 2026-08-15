# Workflow And Examples

### 1. Investigate domain DNS & registration
'''bash
C0rps3> dns target.com
C0rps3> whois target.com
'''
### 2. Check IP infrastructure and geolocation
C0rps3> geo 8.8.8.8
C0rps3> shodan host 8.8.8.8

### 3. People and identity discovery
C0rps3> user johndoe
C0rps3> email target@example.com
C0rps3> phone +14155552671

### 4. Aggregated full footprinting scan
C0rps3> deep domain target.com

### 5. Clear or exit
C0rps3> clear
C0rps3> exit
