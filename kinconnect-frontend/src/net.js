import axios, { AxiosHeaders, AxiosRequestConfig } from 'axios'

function createAuthConfig() {
	return {};
}

const BASE_URL = "https://.."

export async function createProfile( inputFields ) {
    const config = createAuthConfig();
    const { data } = await axios.post( BASE_URL + '/profile', { inputFields }, config );
    return data;
}

export async function search( profile ) {
    const config = createAuthConfig();
    const { data } = await axios.post( BASE_URL + '/search', { profile }, config );
    return data;
}