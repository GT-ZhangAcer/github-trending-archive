const axios = require('axios');
const cheerio = require('cheerio');
const path = require('path');
const { writeFileSync } = require('fs');
const { formatDate } = require('@dwing/common');

function saveFile(targetSrc, fileName, content) {
  const resolve = dir => path.join(__dirname, dir);
  return writeFileSync(resolve(targetSrc + fileName), content, 'utf-8');
}

function crawlData(data) {
  const $ = cheerio.load(data);
  const arr = [];
  $('.Box .Box-row').each((i, elm) => {
    const lang = $(elm).find('[itemprop="programmingLanguage"]');
    const item = {
      title: $(elm)
        .find('h1 a')
        .text()
        .replace(/\s/g, ''),
      url: `https://github.com${$(elm)
        .find('h1 a')
        .attr('href')}`,
      desc: $(elm)
        .find('p')
        .text()
        .trim()
        .replace(/"/g, '')
    };
    if (lang.length !== 0) {
      item.lang = lang.text().replace(/\s/g, '');
    }
    arr.push(item);
  });
  return arr;
}

function formatData(data = [], type) {
  const date = formatDate('yyyy-MM-dd');
  if (type === 'json') {
    return JSON.stringify(data, null, 2);
  }
  if (type === 'markdown') {
    const md = [
      `# ${date}`,
      '',
      ...data.map(({
        title,
        url,
        lang,
        desc
      }, i) => `${i + 1}. [${title}](${url} "${desc}") ${lang === undefined ? '' : `[${lang}]`}`),
      ''
    ];
    return md.join('\n');
  }
  return null;
}


axios.get('https://icors.vercel.app/?https://github.com/trending').then(({ data }) => {
  const date = formatDate('yyyy-MM-dd');
  const arr = crawlData(data);
  saveFile('../spdata/ori_data/', `${date}.json`, formatData(arr, 'json'));
  saveFile('../spdata/ori_archives/', `${date}.md`, formatData(arr, 'markdown'));
});

axios.get('https://icors.vercel.app/?https://github.com/trending?spoken_language_code=zh').then(({ data }) => {
  const date = formatDate('yyyy-MM-dd');
  const arr = crawlData(data);
  saveFile('../spdata/zh_data/', `${date}.json`, formatData(arr, 'json'));
  saveFile('../spdata/zh_archives/', `${date}.md`, formatData(arr, 'markdown'));
});

axios.get('https://icors.vercel.app/?https://github.com/trending/python').then(({ data }) => {
  const date = formatDate('yyyy-MM-dd');
  const arr = crawlData(data);
  saveFile('../spdata/python_data/', `${date}.json`, formatData(arr, 'json'));
  saveFile('../spdata/python_archives/', `${date}.md`, formatData(arr, 'markdown'));
});

axios.get('https://icors.vercel.app/?https://github.com/trending/python?spoken_language_code=zh').then(({ data }) => {
  const date = formatDate('yyyy-MM-dd');
  const arr = crawlData(data);
  saveFile('../spdata/zh_python_data/', `${date}.json`, formatData(arr, 'json'));
  saveFile('../spdata/zh_python_archives/', `${date}.md`, formatData(arr, 'markdown'));
});

