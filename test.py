import requests as rq
host = 'http://127.0.0.1:5000/api'
#r = rq.post(f'{host}/moodle/register', json={'username':'<username>','password':'<password>'})
#r = rq.get(f'{host}'/intiDB?pass=anmrst99', json={'username':'<username>','password':'<password>'})

#r = rq.post(f'{host}/moodle/process_register', json={'username':'<username>','password':'<password>'})
r = rq.post(f'{host}/moodle/bulk', json={'username':'<username>','password':'<password>'})

#r = rq.post(f'{host}/vtop/attendance',json = {'username':'<username>','password':'<password>'})
#r = rq.post(f'{host}'/tgm/cmnd')
#r = rq.post(f'{host}/vtop/bulk',json = {'username':'<username>', 'password':'<password>'})
#r = rq.post(f'{host}/vtop/timetable',json = {'username':'<username>', 'password':'<password>'})
#r = rq.post(f'{host}/vtop/gradelist',json = {'username':'<username>', 'password':'<password>'})
#r = rq.post(f'{host}/vtop/gradecalc',json = {'username':'<username>', 'password':'<password>'})
#r = rq.post(f'{host}/vtop/marks',json = {'username':'<username>', 'password':'<password>'})
#r = rq.post(f'{host}/vtop/attendance',json = {'username':'<username>', 'password':'<password>'})

#print(r)
print(r.text)
