dict={'username': 'admin', 'password' : 'admin', 'home-bg' : 'slider.jpg'}

length=len(dict)
with open('config.json', 'r+') as f:
    f.write('{\n\t\"params\":{\n')
    for key, value in dict.items():
        if length==1:
            f.write(f"\t\t\"{key}\":\"{value}\"\n")
            continue
        else:
            f.write(f"\t\t\"{key}\":\"{value}\",\n")
            length-=1
            continue
    f.write('\t}\n}')
