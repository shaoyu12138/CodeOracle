## 先天八卦常识说明
- 先天八卦的次序是：“乾一、兑二、离三、震四、巽五、坎六、艮七、坤八”。
- 本项目使用标准二进制卦序：乾为000，自下而上变化：“乾、巽、离、艮、兑、坎、震、坤”。
- 为了和二进制兼容，采用0 - 7 数字映射；映射不影响占卜结果，但会更加方便理解和记忆。
- 算卦时，先取下卦，再取上卦。二进制数对应[上卦 下卦]，上卦在高三位，下卦在低三位。

# 高岛易断原理说明
- 本卦获取：使用随机数（模8），先取下卦，再取上卦，拼成一个卦象，对应本卦。
- 动爻获取：使用随机数（根据爻辞数组长度取随机数：模6或7，乾坤有7爻），获取爻数。
- 变卦获取：一爻变后，对应变卦；7爻则直接对应取反。

# 自创六爻卦原理说明（与《焦氏易林》完美匹配，同时与《周易》兼容）
> 以下都是7位二进制数，高位是符号位
- 本卦获取：使用随机数获取一个6位二进制数，第7位根据男（0）女（1）补足，如果是女（1）则全部取反称为规范化得数（本质是获取变卦），得数对应本卦。
- 动爻/变卦获取：根据爻辞数组长度取随机数k，取k位随机二进制数加入到本卦中，获取新的7位二进制数，然后需要规范化后，得数对应本卦。
- 互卦获取：取低6位的二进制数，234->321;345->654位，高位补0。
- 错卦获取：取低6位的二进制数，全位取反，高位补0。
- 综卦获取：取低6位的二进制数，j = n - i + 1 (n = 6;i 是原来的位置;j 是现在的位置)，高位补0。

============================
## 八卦表
乾为000，自下而上变化：
| 序号 | 八卦名称 | 八卦卦象 | 八卦属性 | 二进制数 |
|:-------:|:-----------:|:--------:|:--------:|:--------:|
|    0    |    乾     |   ☰     |    天     |    000   |
|    1    |    巽     |   ☴     |    风     |    001   |
|    2    |    离     |   ☲     |    火     |    010   |
|    3    |    艮     |   ☶     |    山     |    011   |
|    4    |    兑     |   ☱     |    泽     |    100   |
|    5    |    坎     |   ☵     |    水     |    101   |
|    6    |    震     |   ☳     |    雷     |    110   |
|    7    |    坤     |   ☷     |    地     |    111   |

## 六十四卦表
| ID | 6_BIT | 六十四卦名 | 六十四卦象 | 上卦 | 下卦 | 上卦二进制数 | 下卦二进制数 |
|----|-------|------------|------------|------|------|--------------|--------------|
| 0 | 000000 | 乾为天 | ䷀ | 乾 (天) | 乾 (天) | 000 | 000 |
| 1 | 000001 | 天风姤 | ䷫ | 乾 (天) | 巽 (风) | 000 | 001 |
| 2 | 000010 | 天火同人 | ䷌ | 乾 (天) | 离 (火) | 000 | 010 |
| 3 | 000011 | 天山遯 | ䷠ | 乾 (天) | 艮 (山) | 000 | 011 |
| 4 | 000100 | 天泽履 | ䷉ | 乾 (天) | 兑 (泽) | 000 | 100 |
| 5 | 000101 | 天水讼 | ䷅ | 乾 (天) | 坎 (水) | 000 | 101 |
| 6 | 000110 | 天雷无妄 | ䷘ | 乾 (天) | 震 (雷) | 000 | 110 |
| 7 | 000111 | 天地否 | ䷋ | 乾 (天) | 坤 (地) | 000 | 111 |
| 8 | 001000 | 风天小畜 | ䷈ | 巽 (风) | 乾 (天) | 001 | 000 |
| 9 | 001001 | 巽为风 | ䷸ | 巽 (风) | 巽 (风) | 001 | 001 |
| 10 | 001010 | 风火家人 | ䷤ | 巽 (风) | 离 (火) | 001 | 010 |
| 11 | 001011 | 风山渐 | ䷴ | 巽 (风) | 艮 (山) | 001 | 011 |
| 12 | 001100 | 风泽中孚 | ䷼ | 巽 (风) | 兑 (泽) | 001 | 100 |
| 13 | 001101 | 风水涣 | ䷺ | 巽 (风) | 坎 (水) | 001 | 101 |
| 14 | 001110 | 风雷益 | ䷩ | 巽 (风) | 震 (雷) | 001 | 110 |
| 15 | 001111 | 风地观 | ䷓ | 巽 (风) | 坤 (地) | 001 | 111 |
| 16 | 010000 | 火天大有 | ䷍ | 离 (火) | 乾 (天) | 010 | 000 |
| 17 | 010001 | 火风鼎 | ䷱ | 离 (火) | 巽 (风) | 010 | 001 |
| 18 | 010010 | 离为火 | ䷝ | 离 (火) | 离 (火) | 010 | 010 |
| 19 | 010011 | 火山旅 | ䷷ | 离 (火) | 艮 (山) | 010 | 011 |
| 20 | 010100 | 火泽睽 | ䷥ | 离 (火) | 兑 (泽) | 010 | 100 |
| 21 | 010101 | 火水未济 | ䷿ | 离 (火) | 坎 (水) | 010 | 101 |
| 22 | 010110 | 火雷噬嗑 | ䷔ | 离 (火) | 震 (雷) | 010 | 110 |
| 23 | 010111 | 火地晋 | ䷢ | 离 (火) | 坤 (地) | 010 | 111 |
| 24 | 011000 | 山天大畜 | ䷙ | 艮 (山) | 乾 (天) | 011 | 000 |
| 25 | 011001 | 山风蛊 | ䷑ | 艮 (山) | 巽 (风) | 011 | 001 |
| 26 | 011010 | 山火贲 | ䷕ | 艮 (山) | 离 (火) | 011 | 010 |
| 27 | 011011 | 艮为山 | ䷳ | 艮 (山) | 艮 (山) | 011 | 011 |
| 28 | 011100 | 山泽损 | ䷨ | 艮 (山) | 兑 (泽) | 011 | 100 |
| 29 | 011101 | 山水蒙 | ䷃ | 艮 (山) | 坎 (水) | 011 | 101 |
| 30 | 011110 | 山雷颐 | ䷚ | 艮 (山) | 震 (雷) | 011 | 110 |
| 31 | 011111 | 山地剥 | ䷖ | 艮 (山) | 坤 (地) | 011 | 111 |
| 32 | 100000 | 泽天夬 | ䷪ | 兑 (泽) | 乾 (天) | 100 | 000 |
| 33 | 100001 | 泽风大过 | ䷛ | 兑 (泽) | 巽 (风) | 100 | 001 |
| 34 | 100010 | 泽火革 | ䷰ | 兑 (泽) | 离 (火) | 100 | 010 |
| 35 | 100011 | 泽山咸 | ䷞ | 兑 (泽) | 艮 (山) | 100 | 011 |
| 36 | 100100 | 兑为泽 | ䷹ | 兑 (泽) | 兑 (泽) | 100 | 100 |
| 37 | 100101 | 泽水困 | ䷮ | 兑 (泽) | 坎 (水) | 100 | 101 |
| 38 | 100110 | 泽雷随 | ䷐ | 兑 (泽) | 震 (雷) | 100 | 110 |
| 39 | 100111 | 泽地萃 | ䷬ | 兑 (泽) | 坤 (地) | 100 | 111 |
| 40 | 101000 | 水天需 | ䷄ | 坎 (水) | 乾 (天) | 101 | 000 |
| 41 | 101001 | 水风井 | ䷯ | 坎 (水) | 巽 (风) | 101 | 001 |
| 42 | 101010 | 水火既济 | ䷾ | 坎 (水) | 离 (火) | 101 | 010 |
| 43 | 101011 | 水山蹇 | ䷦ | 坎 (水) | 艮 (山) | 101 | 011 |
| 44 | 101100 | 水泽节 | ䷻ | 坎 (水) | 兑 (泽) | 101 | 100 |
| 45 | 101101 | 坎为水 | ䷜ | 坎 (水) | 坎 (水) | 101 | 101 |
| 46 | 101110 | 水雷屯 | ䷂ | 坎 (水) | 震 (雷) | 101 | 110 |
| 47 | 101111 | 水地比 | ䷇ | 坎 (水) | 坤 (地) | 101 | 111 |
| 48 | 110000 | 雷天大壮 | ䷡ | 震 (雷) | 乾 (天) | 110 | 000 |
| 49 | 110001 | 雷风恒 | ䷟ | 震 (雷) | 巽 (风) | 110 | 001 |
| 50 | 110010 | 雷火丰 | ䷶ | 震 (雷) | 离 (火) | 110 | 010 |
| 51 | 110011 | 雷山小过 | ䷽ | 震 (雷) | 艮 (山) | 110 | 011 |
| 52 | 110100 | 雷泽归妹 | ䷵ | 震 (雷) | 兑 (泽) | 110 | 100 |
| 53 | 110101 | 雷水解 | ䷧ | 震 (雷) | 坎 (水) | 110 | 101 |
| 54 | 110110 | 震为雷 | ䷲ | 震 (雷) | 震 (雷) | 110 | 110 |
| 55 | 110111 | 雷地豫 | ䷏ | 震 (雷) | 坤 (地) | 110 | 111 |
| 56 | 111000 | 地天泰 | ䷊ | 坤 (地) | 乾 (天) | 111 | 000 |
| 57 | 111001 | 地风升 | ䷭ | 坤 (地) | 巽 (风) | 111 | 001 |
| 58 | 111010 | 地火明夷 | ䷣ | 坤 (地) | 离 (火) | 111 | 010 |
| 59 | 111011 | 地山谦 | ䷎ | 坤 (地) | 艮 (山) | 111 | 011 |
| 60 | 111100 | 地泽临 | ䷒ | 坤 (地) | 兑 (泽) | 111 | 100 |
| 61 | 111101 | 地水师 | ䷆ | 坤 (地) | 坎 (水) | 111 | 101 |
| 62 | 111110 | 地雷复 | ䷗ | 坤 (地) | 震 (雷) | 111 | 110 |
| 63 | 111111 | 坤为地 | ䷁ | 坤 (地) | 坤 (地) | 111 | 111 |

# 64卦序 (0-63)
0.  乾为天
1.  天风姤
2.  天火同人
3.  天山遯
4.  天泽履
5.  天水讼
6.  天雷无妄
7.  天地否
8.  风天小畜
9.  巽为风
10. 风火家人
11. 风山渐
12. 风泽中孚
13. 风水涣
14. 风雷益
15. 风地观
16. 火天大有
17. 火风鼎
18. 离为火
19. 火山旅
20. 火泽睽
21. 火水未济
22. 火雷噬嗑
23. 火地晋
24. 山天大畜
25. 山风蛊
26. 山火贲
27. 艮为山
28. 山泽损
29. 山水蒙
30. 山雷颐
31. 山地剥
32. 泽天夬
33. 泽风大过
34. 泽火革
35. 泽山咸
36. 兑为泽
37. 泽水困
38. 泽雷随
39. 泽地萃
40. 水天需
41. 水风井
42. 水火既济
43. 水山蹇
44. 水泽节
45. 坎为水
46. 水雷屯
47. 水地比
48. 雷天大壮
49. 雷风恒
50. 雷火丰
51. 雷山小过
52. 雷泽归妹
53. 雷水解
54. 震为雷
55. 雷地豫
56. 地天泰
57. 地风升
58. 地火明夷
59. 地山谦
60. 地泽临
61. 地水师
62. 地雷复
63. 坤为地

## 分类
> 下面是提取上表并排序的六十四卦名，序号从1开始，并按上卦（天、风、火、山、泽、水、雷、地）每8个一组排列：

天 (上卦)
1.  乾为天
2.  天风姤
3.  天火同人
4.  天山遯
5.  天泽履
6.  天水讼
7.  天雷无妄
8.  天地否

风 (上卦)
9.  风天小畜
10. 巽为风
11. 风火家人
12. 风山渐
13. 风泽中孚
14. 风水涣
15. 风雷益
16. 风地观

火 (上卦)
17. 火天大有
18. 火风鼎
19. 离为火
20. 火山旅
21. 火泽睽
22. 火水未济
23. 火雷噬嗑
24. 火地晋

山 (上卦)
25. 山天大畜
26. 山风蛊
27. 山火贲
28. 艮为山
29. 山泽损
30. 山水蒙
31. 山雷颐
32. 山地剥

泽 (上卦)
33. 泽天夬
34. 泽风大过
35. 泽火革
36. 泽山咸
37. 兑为泽
38. 泽水困
39. 泽雷随
40. 泽地萃

水 (上卦)
41. 水天需
42. 水风井
43. 水火既济
44. 水山蹇
45. 水泽节
46. 坎为水
47. 水雷屯
48. 水地比

雷 (上卦)
49. 雷天大壮
50. 雷风恒
51. 雷火丰
52. 雷山小过
53. 雷泽归妹
54. 雷水解
55. 震为雷
56. 雷地豫

地 (上卦)
57. 地天泰
58. 地风升
59. 地火明夷
60. 地山谦
61. 地泽临
62. 地水师
63. 地雷复
64. 坤为地