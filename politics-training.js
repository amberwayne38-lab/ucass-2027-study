// Use the existing question IDs, history and retry controls for all practice.
function politicsQuestions(points) {
  return points.flatMap(point => {
    const common = {
      s: 'politics', topic: point.course + ' · ' + point.chapter,
      origin: '原创', reviewStatus: '已核对教材章节',
      src: [point.source, ...point.otherSources].join('；')
    };
    return [
      {...common, id: point.id + '-choice', kind: 'mcq', typeGroup: '选择题',
       t: point.concept, p: point.question, o: point.options,
       k: point.options.indexOf(point.answer), exp: point.explanation},
      {...common, id: point.id + '-recall', kind: 'flash', typeGroup: '背诵自测',
       t: point.concept, p: point.recall, answer: point.recallAnswer}
    ];
  });
}
