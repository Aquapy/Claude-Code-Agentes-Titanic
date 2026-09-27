"""Fase 1 - Limpieza. Lee titanic.csv (sin modificarlo) y genera outputs/titanic_clean.csv.
Uso: python scripts/01_limpieza.py  (funciona desde cualquier carpeta)"""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT); os.makedirs("outputs", exist_ok=True)
import pandas as pd, numpy as np, hashlib
src='titanic.csv'
h0=hashlib.md5(open(src,'rb').read()).hexdigest()
raw=pd.read_csv(src)
df=raw.copy()
log=[]
def sh(step): log.append((step,df.shape)); print(step,df.shape)
sh('carga')
nulls_before=raw.isna().sum()
# espacios
n_strip=int((df.Name!=df.Name.str.strip()).sum())
for c in ['Name','Sex','Ticket','Cabin','Embarked']:
    df[c]=df[c].str.strip()
sh('strip espacios')
# Embarked
emb_rows=df.index[df.Embarked.isna()].tolist()
moda=df.Embarked.mode()[0]
df['Embarked']=df.Embarked.fillna(moda)
sh('imputar Embarked')
# Age
df['Age_imputada']=df.Age.isna().astype(int)
med_global=df.Age.median()
grp=df.groupby(['Pclass','Sex'],observed=True).Age.median()
print(grp)
df['Age']=df.Age.fillna(df.groupby(['Pclass','Sex']).Age.transform('median'))
assert df.Age.isna().sum()==0
sh('imputar Age')
# Cabin
df['tiene_Cabin']=df.Cabin.notna().astype(int)
df['Deck']=df.Cabin.str[0].fillna('Desconocido')
sh('indicadores Cabin')
# Tipos
df['PassengerId']=df.PassengerId.astype(str)
for c in ['Survived','Pclass','Sex','Embarked','Deck']: df[c]=df[c].astype('category')
df['Survived']=df.Survived.astype(int) if False else df.Survived
sh('tipos')
assert len(df)==891 and df.PassengerId.is_unique
assert df[['Age','Embarked','Fare','Deck']].isna().sum().sum()==0
df.to_csv('outputs/titanic_clean.csv',index=False)
chk=pd.read_csv('outputs/titanic_clean.csv',dtype={'PassengerId':str})
print(chk.shape, chk.isna().sum().to_dict(), df.dtypes.to_dict())
assert hashlib.md5(open(src,'rb').read()).hexdigest()==h0
nulls_after=df.isna().sum()
# stats
print('Age antes/despues mean',raw.Age.mean(),df.Age.mean(),'median',raw.Age.median(),df.Age.median())
print(df.Deck.value_counts().to_dict())
fare0=raw[raw.Fare==0]; print(fare0.Pclass.value_counts().to_dict(), fare0.Survived.mean(), fare0.Embarked.value_counts().to_dict())
q1,q3=raw.Fare.quantile([.25,.75]); print('fare iqr limit',q3+1.5*(q3-q1))
print(raw[raw.Fare>500][['PassengerId','Name','Fare','Pclass','Ticket']])
print(raw[raw.Age>=70][['PassengerId','Age']].shape, raw.Age.max(), raw.Age.min(), (raw.Age<1).sum())
print(raw[raw.SibSp>=5].shape, raw[raw.Parch>=5].shape)
tk=raw.groupby('Ticket').size(); print('tickets compartidos',(tk>1).sum(), 'filas',tk[tk>1].sum())
print(raw[raw.duplicated(['Name'],keep=False)].shape, raw.duplicated(['Ticket','Cabin','Fare','Pclass'],keep=False).sum())
print('surv por tiene_Cabin',chk.groupby('tiene_Cabin').Survived.mean().to_dict())
print('surv por Age_imputada',chk.groupby('Age_imputada').Survived.mean().to_dict())
print('emb',raw[raw.Embarked.isna()][['PassengerId','Name','Ticket','Cabin']].to_dict('records'))
print(n_strip, emb_rows, moda, h0)
print(raw.Name[raw.Name!=raw.Name.str.strip()].tolist())
