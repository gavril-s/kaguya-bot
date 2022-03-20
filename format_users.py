import io

inp = io.open('users.json', mode='r').read()
out = io.open('formatted_users.json', mode='w', encoding='utf-8')

for i in inp:
    out.write(i)
    if i in ',{}[]':
        out.write('\n')