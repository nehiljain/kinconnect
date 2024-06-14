
export default function SummaryEditor({ summaryData, onMatchResults }) {

	const onSearch = () => {
		onMatchResults({ matches: [] });
	}

	return (
		<div>
			<h2>Search</h2>
        	<button onClick={onSearch}>Search</button>
		</div>
	)
}