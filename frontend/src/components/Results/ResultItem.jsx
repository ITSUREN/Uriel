function ResultItem({ result }) {
  const { title, score, snippet, path } = result;

  return (
    <div>
      <h3>{title}</h3>
      <p>Score: {score}</p>
      <p>{snippet}</p>
      <p>{path}</p>
    </div>
  );
}

export default ResultItem;