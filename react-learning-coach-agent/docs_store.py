from typing import List, Dict

DOCS: List[Dict[str, str]] = [
    {
        "topic": "jsx basics",
        "content": "JSX lets you write HTML-like syntax in React components. Each component returns JSX from its render function...",
        "link": "https://react.dev/learn/writing-markup-with-jsx",
    },
    {
        "topic": "props vs state",
        "content": "Props are read-only inputs to components, passed from parent. State is local and managed inside a component using hooks like useState...",
        "link": "https://react.dev/learn/state-a-components-memory",
    },
    {
        "topic": "useState hook",
        "content": "useState lets you add state to function components: const [value, setValue] = useState(initial)...",
        "link": "https://react.dev/reference/react/useState",
    },
    {
        "topic": "useEffect hook",
        "content": "useEffect lets you run side effects in function components, like fetching data or subscribing to events...",
        "link": "https://react.dev/reference/react/useEffect",
    },
    {
        "topic": "react router",
        "content": "React Router is a library for client-side routing in React apps...",
        "link": "https://reactrouter.com/en/main/start/tutorial",
    },
]
