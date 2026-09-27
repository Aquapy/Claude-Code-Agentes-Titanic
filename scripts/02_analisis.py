"""Fase 2 - Analisis exploratorio. Lee outputs/titanic_clean.csv y escribe outputs/tables/*.csv.
Uso: python scripts/02_analisis.py  (funciona desde cualquier carpeta)"""
import pandas as pd, numpy as np, os
from scipy import stats
import statsmodels.formula.api as smf
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30); pd.set_option('display.max_rows', 200)
from pathlib import Path
B = str(Path(__file__).resolve().parents[1] / 'outputs') + '/'
T = B + 'tables/'
os.makedirs(T, exist_ok=True)
d = pd.read_csv(B + 'titanic_clean.csv', dtype={'PassengerId': str})


def rate(df, by):
    g = df.groupby(by, observed=True)['Survived'].agg(n='size', supervivientes='sum', tasa='mean')
    g['tasa_pct'] = (g.tasa * 100).round(1)
    return g.drop(columns='tasa').reset_index()


def chi(df, col):
    ct = pd.crosstab(df[col], df.Survived)
    c, p, dof, _ = stats.chi2_contingency(ct)
    return round(c, 2), p, dof


def cv(df, col):
    ct = pd.crosstab(df[col], df.Survived)
    c = stats.chi2_contingency(ct, correction=False)[0]
    return np.sqrt(c / ct.values.sum() / (min(ct.shape) - 1))


print('N', len(d), d.Survived.mean())
for col in ['Sex', 'Pclass', 'Embarked', 'SibSp', 'Parch', 'tiene_Cabin', 'Age_imputada']:
    r = rate(d, col); print('\n', col); print(r)
    c, p, dof = chi(d, col); print('chi2=%.2f dof=%d p=%.3g V=%.3f' % (c, dof, p, cv(d, col)))
rate(d, 'Sex').to_csv(T + 'tasa_por_sexo.csv', index=False)
rate(d, 'Pclass').to_csv(T + 'tasa_por_clase.csv', index=False)
rate(d, 'Embarked').to_csv(T + 'tasa_por_embarque.csv', index=False)
d['Familia'] = d.SibSp + d.Parch + 1
d['Fam_grupo'] = pd.cut(d.Familia, [0, 1, 4, 20], labels=['Solo (1)', '2-4', '5+']).astype(str)
r = rate(d, 'Fam_grupo'); print(r); print(chi(d, 'Fam_grupo'))
rate(d, 'Familia').to_csv(T + 'tasa_por_tamano_familia.csv', index=False)
r.to_csv(T + 'tasa_por_grupo_familia.csv', index=False)
print(rate(d, 'Familia'))
sp = rate(d, ['Pclass', 'Sex']); print(sp); sp.to_csv(T + 'tasa_clase_x_sexo.csv', index=False)
for pc in [1, 2, 3]:
    s = d[d.Pclass == pc]; print('Pclass', pc, 'sexo chi2', chi(s, 'Sex'))
for sx in ['female', 'male']:
    s = d[d.Sex == sx]; print(sx, 'clase chi2', chi(s, 'Pclass'))

# Age
for lab, df in [('completo', d), ('solo_reales', d[d.Age_imputada == 0])]:
    df = df.copy()
    df['Edad_grupo'] = pd.cut(df.Age, [0, 12, 18, 35, 50, 80], labels=['0-12', '13-18', '19-35', '36-50', '51+']).astype(str)
    r = rate(df, 'Edad_grupo'); print('\nAge bins', lab); print(r)
    print('chi', chi(df, 'Edad_grupo'))
    a = df[df.Survived == 1].Age; b = df[df.Survived == 0].Age
    print('Age surv med %.1f (n=%d) vs no med %.1f (n=%d) mean %.2f vs %.2f MW p=%.3g Welch p=%.3g' % (
        a.median(), len(a), b.median(), len(b), a.mean(), b.mean(), stats.mannwhitneyu(a, b).pvalue,
        stats.ttest_ind(a, b, equal_var=False).pvalue))
    r.to_csv(T + 'tasa_por_edad_%s.csv' % lab, index=False)
    df['nino'] = (df.Age <= 12).astype(int)
    print(rate(df, 'nino')); print(chi(df, 'nino'))
    rs = rate(df, ['Sex', 'Edad_grupo']); print(rs)
    rs.to_csv(T + 'tasa_sexo_x_edad_%s.csv' % lab, index=False)
    print(df.groupby('Pclass').Age.agg(['size', 'mean', 'median']))
    print(rate(df, ['Pclass', 'Edad_grupo']))
real = d[d.Age_imputada == 0].copy()
print('ninos<=12 real por clase'); print(rate(real[real.Age <= 12], ['Pclass']))
print(rate(real[real.Age <= 12], ['Sex']))
print(pd.crosstab(d.Pclass, d.Age_imputada))
print(rate(d, ['Pclass', 'Age_imputada']))
for pc in [1, 2, 3]:
    for sx in ['female', 'male']:
        s = real[(real.Pclass == pc) & (real.Sex == sx)]
        a = s[s.Survived == 1].Age; b = s[s.Survived == 0].Age
        s2 = d[(d.Pclass == pc) & (d.Sex == sx)]
        a2 = s2[s2.Survived == 1].Age; b2 = s2[s2.Survived == 0].Age
        print(pc, sx, 'real', len(a), len(b), '%.1f %.1f p=%.3g' % (a.median(), b.median(), stats.mannwhitneyu(a, b).pvalue),
              '| completo', len(a2), len(b2), '%.1f %.1f p=%.3g' % (a2.median(), b2.median(), stats.mannwhitneyu(a2, b2).pvalue))
# Age x Sex table for real & full for menores
print('hombres real edad grupos')
rr = real.copy(); rr['Edad_grupo'] = pd.cut(rr.Age, [0, 12, 18, 35, 50, 80], labels=['0-12', '13-18', '19-35', '36-50', '51+']).astype(str)
print(rate(rr[rr.Sex == 'male'], 'Edad_grupo'))

# Fare
d['Fare_cuartil'] = pd.qcut(d.Fare, 4, labels=['Q1', 'Q2', 'Q3', 'Q4']).astype(str)
r = rate(d, 'Fare_cuartil'); print(r); r.to_csv(T + 'tasa_por_cuartil_tarifa.csv', index=False)
print(d.groupby('Fare_cuartil').Fare.agg(['min', 'max']))
print(chi(d, 'Fare_cuartil'))
a = d[d.Survived == 1].Fare; b = d[d.Survived == 0].Fare
print('Fare med', a.median(), b.median(), 'mean', a.mean(), b.mean(), stats.mannwhitneyu(a, b).pvalue)
print(rate(d, ['Pclass', 'Fare_cuartil']))
for pc in [1, 2, 3]:
    s = d[d.Pclass == pc]; a = s[s.Survived == 1].Fare; b = s[s.Survived == 0].Fare
    print('Fare within class', pc, len(a), len(b), a.median(), b.median(), stats.mannwhitneyu(a, b).pvalue)
    print(s.Fare.describe()[['min', '50%', 'max']].values)
print(d.groupby('Pclass').Fare.agg(['size', 'median', 'mean']))
d['Fare0'] = (d.Fare == 0).astype(int)
print(rate(d, 'Fare0')); print(d[d.Fare == 0][['PassengerId', 'Survived', 'Pclass', 'Sex', 'Age', 'Embarked', 'Age_imputada']])
print('sin fare0 por clase'); print(rate(d[d.Fare > 0], 'Pclass'))
print('fare0 por clase'); print(rate(d[d.Fare == 0], 'Pclass'))
d['tk_n'] = d.groupby('Ticket').Ticket.transform('size'); d['Fare_pp'] = d.Fare / d.tk_n
print(d.tk_n.value_counts().sort_index())
d['Fare_pp_cuartil'] = pd.qcut(d.Fare_pp, 4, labels=['Q1', 'Q2', 'Q3', 'Q4']).astype(str)
print(rate(d, 'Fare_pp_cuartil'))
print('rho Fare', stats.spearmanr(d.Fare, d.Survived), 'rho Fare_pp', stats.spearmanr(d.Fare_pp, d.Survived))
for pc in [1, 2, 3]:
    s = d[d.Pclass == pc]
    print(pc, 'rho fare_pp within class', stats.spearmanr(s.Fare_pp, s.Survived), 'rho fare', stats.spearmanr(s.Fare, s.Survived))
d['tk_grp'] = pd.cut(d.tk_n, [0, 1, 2, 4, 20], labels=['1', '2', '3-4', '5+']).astype(str)
print(rate(d, 'tk_grp'))
# Cabin / Deck
cc = rate(d, ['Pclass', 'tiene_Cabin']); print(cc); cc.to_csv(T + 'tasa_clase_x_cabina.csv', index=False)
for pc in [1, 2, 3]:
    s = d[d.Pclass == pc]
    ct = pd.crosstab(s.tiene_Cabin, s.Survived)
    print('cabin within', pc, 'chi p=%.3g' % stats.chi2_contingency(ct)[1], 'fisher', stats.fisher_exact(ct))
print(rate(d[d.tiene_Cabin == 1], 'Deck'))
cd = rate(d[d.tiene_Cabin == 1], ['Pclass', 'Deck']); print(cd); cd.to_csv(T + 'tasa_clase_x_deck.csv', index=False)
print(pd.crosstab(d.Pclass, d.tiene_Cabin, normalize='index'))
cs = rate(d, ['Pclass', 'Sex', 'tiene_Cabin']); print(cs); cs.to_csv(T + 'tasa_clase_sexo_cabina.csv', index=False)
# Embarked
print(pd.crosstab(d.Embarked, d.Pclass)); print(rate(d, ['Pclass', 'Embarked'])); print(rate(d, ['Sex', 'Embarked']))
rate(d, ['Pclass', 'Embarked']).to_csv(T + 'tasa_clase_x_embarque.csv', index=False)
for pc in [1, 2, 3]:
    s = d[d.Pclass == pc]; print('emb within', pc, chi(s, 'Embarked'))
# sin passengers 62 y 830
print('sin 62 y 830 embarque'); print(rate(d[~d.PassengerId.isin(['62', '830'])], 'Embarked'))
# Family
print(rate(d, ['Sex', 'Fam_grupo'])); print(rate(d, ['Pclass', 'Fam_grupo']))
for pc in [1, 2, 3]:
    s = d[d.Pclass == pc]; print('fam within', pc, chi(s, 'Fam_grupo'))
rate(d, ['Pclass', 'Fam_grupo']).to_csv(T + 'tasa_clase_x_grupo_familia.csv', index=False)
# correlations
num = d[['Survived', 'Pclass', 'Age', 'SibSp', 'Parch', 'Fare', 'tiene_Cabin', 'Age_imputada']].copy()
num['Sex_female'] = (d.Sex == 'female').astype(int); num['Familia'] = d.Familia
cm = num.corr(method='spearman').round(3); print(cm); cm.to_csv(T + 'correlaciones_spearman.csv')
# logistic
d['fem'] = (d.Sex == 'female').astype(int)
real = d[d.Age_imputada == 0].copy()
m = smf.logit('Survived ~ C(Pclass)+fem+Age+Familia', data=d).fit(disp=0); print(m.summary2().tables[1]); print('pseudoR2', m.prsquared)
m2 = smf.logit('Survived ~ C(Pclass)+fem+Age+Familia', data=real).fit(disp=0); print(m2.summary2().tables[1])
m3 = smf.logit('Survived ~ C(Pclass)+fem+Age+Familia+C(Embarked)+tiene_Cabin', data=d).fit(disp=0); print(m3.summary2().tables[1])


def orci(m, name):
    t = pd.DataFrame({'OR': np.exp(m.params), 'IC95_inf': np.exp(m.conf_int()[0]), 'IC95_sup': np.exp(m.conf_int()[1]), 'p': m.pvalues}).round(4)
    t['modelo'] = name; t['n'] = int(m.nobs)
    return t.reset_index().rename(columns={'index': 'variable'})


pd.concat([orci(m, 'completo'), orci(m2, 'solo_edad_real'), orci(m3, 'completo_ampliado')]).to_csv(T + 'regresion_logistica_OR.csv', index=False)
print(rate(d, ['Sex', 'Pclass']).sort_values('tasa_pct'))
