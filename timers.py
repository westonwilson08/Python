#script used in a CTF event to compile multiple time-based urls to get all details at once
import requests
pt1 = 'https://ctf.url/challenge-files/clock-pt1?verify=kA3Sji1gAM6bFU677EenmA%3D%3D'
pt2 = 'https://ctf.url/challenge-files/clock-pt2?verify=kA3Sji1gAM6bFU677EenmA%3D%3D'
pt3 = 'https://ctf.url/challenge-files/clock-pt3?verify=kA3Sji1gAM6bFU677EenmA%3D%3D'
pt4 = 'https://ctf.url/challenge-files/clock-pt4?verify=kA3Sji1gAM6bFU677EenmA%3D%3D'
pt5 = 'https://ctf.url/challenge-files/clock-pt5?verify=kA3Sji1gAM6bFU677EenmA%3D%3D'
validate = 'ctf.url/challenge-files/get-flag?verify=kA3Sji1gAM6bFU677EenmA%3D%3D&string='

part1 = requests.get(pt1)
part2 = requests.get(pt2)
part3 = requests.get(pt3)
part4 = requests.get(pt4)
part5 = requests.get(pt5)

full = part1.text+part2.text+part3.text+part4.text+part5.text
print(full)
validate = validate + full
val = requests.get(validate)
print(val.text)
