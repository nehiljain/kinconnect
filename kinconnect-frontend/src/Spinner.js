import React from 'react'
import FadeLoader from 'react-spinners/FadeLoader'

const override = { // :CSSProperties
    display: "block",
    margin: "0 auto",
};

/*
interface Props {
    visible: boolean;
    label?: string,
    style?: any
}*/

export default function Spinner({ visible, label = 'Loading', style = {} }) {
	const combined = {...Style.spinner,...style}
    return (
        <div style={combined}>
            <FadeLoader
                color={'#666'}
                loading={visible}
                cssOverride={override}
                aria-label={label}
                data-testid="loader"
            />
        </div>
    );
}

const Style = {
    spinner: {
        width: '100%'
    }
};