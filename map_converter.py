BASE_DIR = "F:\\Kro\\kRO_FullClient_20200409\\data\\"
TARGET_DIR = "G:/TargetRO/data/"

import os
import struct
import json

def read(f, t):
    d = {'b':1,'i':4,'f':4,'s':1}
    qt = t[:-1]
    if(qt):
        d[t] = int(qt)
    v = struct.unpack(t, (f.read(d[t])))[0]
    return v# if(not 's' in t) else v.decode('iso-8859-1')
    
        
class RSWFile():
    def isCompatible(self, a, i):
        return ((self.data['Header']['Major Version'] == a and self.data['Header']['Minor Version'] >= i) or self.data['Header']['Major Version'] > a)
    def __init__(self, file_name, only_ver = None):
        
        with open(file_name, 'rb') as f:    
            self.end_file = f.seek(0, 2)
        
        with open(file_name, 'rb') as f:
            f.read(4) #GRSW
            self.data = {
                'Header':{
                    'Major Version': read(f,'b'),
                    'Minor Version': read(f,'b')
                },
                'Water' : {},
                'Light' : {},
                'Some Bullshit' : {},
                'Objs' : []
            }
            self.obj_type = {
                1: 'Model',
                2: 'Light',
                3: 'Sound',
                4: 'Effect'
            }
            self.data['Header']['Original Ver'] = (self.data['Header']['Major Version'], self.data['Header']['Minor Version'])
            if(not (only_ver is None or self.data['Header']['Original Ver'] == only_ver) ):
                self.data = None
                return
            
            if (self.isCompatible(2, 5)):
                self.data['Header'].update({'BuildNumber':read(f,'i')})
			
            if (self.isCompatible(2, 2)):
                self.data['Header'].update({'UnknownData':read(f,'b')})

            self.data['Header'].update({'IniFile':read(f,'40s')})
            self.data['Header'].update({'GroundFile':read(f,'40s')})

            if (self.isCompatible(1, 4)):
                self.data['Header'].update({'AltitudeFile':read(f,'40s')})

            self.data['Header'].update({'SourceFile':read(f,'40s')})



            if (not self.isCompatible(2, 6)):

                if (self.isCompatible(1, 3)):
                    self.data['Water'].update({'Level':read(f,'f')})

                if (self.isCompatible(1, 8)):
                    self.data['Water'].update({'Type':read(f,'i')})
                    self.data['Water'].update({'WaveHeight':read(f,'f')})
                    self.data['Water'].update({'WaveSpeed':read(f,'f')})
                    self.data['Water'].update({'WavePitch':read(f,'f')})

                if (self.isCompatible(1, 9)):
                    self.data['Water'].update({'TextureCycling':read(f,'i')})
            
            if (self.isCompatible(1, 5)):
                self.data['Light'].update({'Longitude':read(f,'i')})
                self.data['Light'].update({'Latitude':read(f,'i')})
                self.data['Light'].update({'DiffuseRed':read(f,'f')})
                self.data['Light'].update({'DiffuseGreen':read(f,'f')})
                self.data['Light'].update({'DiffuseBlue':read(f,'f')})
                self.data['Light'].update({'AmbientRed':read(f,'f')})
                self.data['Light'].update({'AmbientGreen':read(f,'f')})
                self.data['Light'].update({'AmbientBlue':read(f,'f')})
            
            if (self.isCompatible(1, 7)):
                self.data['Light'].update({'Ignored':read(f,'f')})

            if (self.isCompatible(1, 6)):
                self.data['Some Bullshit'] = read(f,'16s')
            
            self.data['Qt Objetos'] = read(f,'i')
            for _ in range(self.data['Qt Objetos']):
                to = read(f,'i')
                t = self.obj_type[to]
                self.data['Objs'].append(eval('self.%s_read(f)'%t))
                self.data['Objs'][-1]['Type_num'] = to

            if (f.tell() != self.end_file and self.isCompatible(2, 1)):
                self.data['NonSense Bullshit'] = f.read()


    def Model_read(self, reader):
        model = {'Type':'Model'}
        if (self.isCompatible(1, 3)):
            model['Name'] = reader.read(40)
            model['AnimationType'] = read(reader,'i')
            model['AnimationSpeed'] = read(reader,'i')

            if (model['AnimationSpeed'] < 0 or model['AnimationSpeed'] >= 100):
                model['AnimationSpeed'] = 1

            model['BlockType'] = read(reader,'i')

            if (self.isCompatible(2, 6) and self.data['Header']['BuildNumber'] >= 186):
                model['Unknown'] = read(reader,'b')

        model['ModelName'] = (read(reader,'80s'))
        model['NodeName'] = (read(reader,'80s'))

        model['Position'] = (read(reader,'f'), read(reader,'f'), read(reader,'f'))
        model['Rotation'] = (read(reader,'f'), read(reader,'f'), read(reader,'f'))
        model['Scale'] = (read(reader,'f'), read(reader,'f'), read(reader,'f'))
        
        return model


    def Light_read(self,reader):
        light = {'Type':'Light'}
        light['Name'] = (read(reader,'80s'))
        light['Position'] = (read(reader,'f'), read(reader,'f'), read(reader,'f'))
        light['Color'] = (255, read(reader,'i'), read(reader,'i'), read(reader,'i'))
        light['Range'] = read(reader,'f')
        return light
                

    def Sound_read(self,reader):
        sound = {'Type':'Sound'}
        sound['Name'] = (read(reader,'80s'))
        sound['WaveName'] = (read(reader,'80s'))
        sound['Position'] = (read(reader,'f'), read(reader,'f'), read(reader,'f'))
        sound['Volume'] = read(reader,'f')
        sound['Width'] = read(reader,'i')
        sound['Height'] = read(reader,'i')
        sound['Range'] = read(reader,'f')

        if (self.isCompatible(2, 0)):
            sound['Cycle'] = read(reader,'f')
        elif (self.isCompatible(1, 9)):
            if (reader.tell() != self.end_file):
                possibleType = read(reader,'i')
                reader.seek(reader.tell()-4)

                if (possibleType < 1 or possibleType > 4):
                    sound['Cycle'] = read(reader,'f')
        return sound
    
    def Effect_read(self,reader):
        effect = {'Type':'Effect'}
        effect['Name'] = (read(reader,'80s'))
        effect['Position'] = (read(reader,'f'), read(reader,'f'), read(reader,'f'))
        effect['EffectNumber'] = read(reader,'i')
        effect['EmitSpeed'] = read(reader,'f')
        effect['Param'] = (read(reader,'f'), read(reader,'f'), read(reader,'f'), read(reader,'f'))

        return effect
    
    def save(self, file_name, ver, aditional_info = None):
        if(not aditional_info is None):
            self.data.update(aditional_info)
        
        with open(file_name, 'wb') as f:
            f.write(b'GRSW')
            self.data['Header']['Major Version'], self.data['Header']['Minor Version'] = ver
            
            f.write(struct.pack('bb',*ver))
        

            if (self.isCompatible(2, 5)):
                f.write(struct.pack('i',self.data['Header']['BuildNumber']))
			
            if (self.isCompatible(2, 2)):
                f.write(struct.pack('b',self.data['Header']['UnknownData']))

            f.write(struct.pack('40s',self.data['Header']['IniFile']))
            f.write(struct.pack('40s',self.data['Header']['GroundFile']))

            if (self.isCompatible(1, 4)):
                f.write(struct.pack('40s',self.data['Header']['AltitudeFile']))

            f.write(struct.pack('40s',self.data['Header']['SourceFile']))

            if (not self.isCompatible(2, 6)):

                if (self.isCompatible(1, 3)):
                    f.write(struct.pack('f',self.data['Water']['Level']))

                if (self.isCompatible(1, 8)):
                    f.write(struct.pack('i',self.data['Water']['Type']))
                    f.write(struct.pack('f',self.data['Water']['WaveHeight']))
                    f.write(struct.pack('f',self.data['Water']['WaveSpeed']))
                    f.write(struct.pack('f',self.data['Water']['WavePitch']))
                    
                if (self.isCompatible(1, 9)):
                    f.write(struct.pack('i',self.data['Water']['TextureCycling']))
            
            if (self.isCompatible(1, 5)):
                f.write(struct.pack('i',self.data['Light']['Longitude']))
                f.write(struct.pack('i',self.data['Light']['Latitude']))
                
                f.write(struct.pack('f',self.data['Light']['DiffuseRed']))
                f.write(struct.pack('f',self.data['Light']['DiffuseGreen']))
                f.write(struct.pack('f',self.data['Light']['DiffuseBlue']))
                f.write(struct.pack('f',self.data['Light']['AmbientRed']))
                f.write(struct.pack('f',self.data['Light']['AmbientGreen']))
                f.write(struct.pack('f',self.data['Light']['AmbientBlue']))
            
            if (self.isCompatible(1, 7)):
                f.write(struct.pack('f',self.data['Light']['Ignored']))

            if (self.isCompatible(1, 6)):
                f.write(struct.pack('16s',self.data['Some Bullshit']))
            
            f.write(struct.pack('i',self.data['Qt Objetos']))
            for obj in self.data['Objs']:
                f.write(struct.pack('i',obj['Type_num']))
                eval('self.%s_write(f, obj)'%obj['Type'])

            if ('NonSense Bullshit' in self.data and self.isCompatible(2, 1)):
                f.write(self.data['NonSense Bullshit'])


    def Model_write(self, w, obj):
        if (self.isCompatible(1, 3)):
            w.write(obj['Name'])
            w.write(struct.pack('i',obj['AnimationType']))
            w.write(struct.pack('i',obj['AnimationSpeed']))
            w.write(struct.pack('i',obj['BlockType']))

            if (self.isCompatible(2, 6) and self.data['Header']['BuildNumber'] >= 186):
                w.write(struct.pack('b',obj['Unknown']))

        w.write(obj['ModelName'])
        w.write(obj['NodeName'])

        w.write(struct.pack('fff',*obj['Position']))
        w.write(struct.pack('fff',*obj['Rotation']))
        w.write(struct.pack('fff',*obj['Scale']))

    def Light_write(self, w, obj):
        w.write(obj['Name'])
        w.write(struct.pack('fff',*obj['Position']))
        w.write(struct.pack('iii',*obj['Color'][1:]))
        w.write(struct.pack('f',obj['Range']))
                

    def Sound_write(self, w, obj):
        w.write(obj['Name'])
        w.write(obj['WaveName'])
        w.write(struct.pack('fff',*obj['Position']))
        w.write(struct.pack('f',obj['Volume']))
        w.write(struct.pack('i',obj['Width']))
        w.write(struct.pack('i',obj['Height']))
        w.write(struct.pack('f',obj['Range']))

        if (self.isCompatible(1, 9)):
            w.write(struct.pack('f',obj['Cycle']))
    
    def Effect_write(self, w, obj):
        w.write(obj['Name'])
        w.write(struct.pack('fff',*obj['Position']))
        w.write(struct.pack('i',obj['EffectNumber']))
        w.write(struct.pack('f',obj['EmitSpeed']))
        w.write(struct.pack('ffff',*obj['Param']))


with open('meta_maps.json', 'r') as f:
    aditional_info = json.load(f)

file_list = [v.replace('.rsw','') for v in os.listdir(BASE_DIR) if '.rsw' in v]

for file_name in file_list:
    f = RSWFile(BASE_DIR+file_name+'.rsw', only_ver=(2,6))
    if(f.data is not None):
        print(f"Converting {file_name}")
        map_name = file_name.replace('\\','/').split('/')[-1].split('.')[0]
        f.save(TARGET_DIR+file_name+'.rsw', (1,9), aditional_info.get(map_name, aditional_info['default']))
        # .GAT ver 1.02
        with open(TARGET_DIR+file_name+'.gat', 'wb') as w:
            with open(BASE_DIR+file_name+'.gat', 'rb') as r:
                w.write(r.read(4))
                r.read(2)
                w.write(b'\x01\x02')
                w.write(r.read())
        # .GND ver 1.07
        with open(TARGET_DIR+file_name+'.gnd', 'wb') as w:
            with open(BASE_DIR+file_name+'.gnd', 'rb') as r:
                w.write(r.read(4))
                r.read(2)
                w.write(b'\x01\x07')
                w.write(r.read())
            
