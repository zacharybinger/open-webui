<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
    import { WEBUI_API_BASE_URL } from '$lib/constants';

	const i18n = getContext<Writable<i18nType>>('i18n');

	export let message;
	export let chatId;

	let submitting = false;
	let formData = {};

	// Elicitation structure typically has type, title, schema, etc.
    // e.g. message.elicitation.params.creation or message.elicitation.elicitation
    $: elicitation = message?.elicitation?.data?.params?.creation || message?.elicitation?.data || message?.elicitation;

	$: schema = elicitation?.schema || elicitation?.requestedSchema || {};
	$: properties = schema?.properties || {};
	$: requiredFields = schema?.required || [];

	const resolveElicitation = async (action: 'accept' | 'decline' | 'cancel', data: any = null) => {
		submitting = true;
        // In the backend, the endpoint receives action, data
        const request_id = message?.elicitation?.id || message?.id; // If wait, where is request_id?
		try {
			const res = await fetch(`${WEBUI_API_BASE_URL}/mcp/elicitation/${request_id}`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${localStorage.token}`
				},
				body: JSON.stringify({
					action,
					data
				})
			});

			if (res.ok) {
				toast.success($i18n.t('Response submitted'));
			} else {
                const err = await res.json();
				toast.error(err.detail || $i18n.t('Failed to submit response'));
			}
		} catch (error) {
			toast.error($i18n.t('Failed to submit response'));
		} finally {
			submitting = false;
		}
	};

	const handleSubmit = () => {
		resolveElicitation('accept', formData);
	};
</script>

{#if elicitation}
	<div class="my-3 p-4 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-850">
		<h3 class="font-medium text-lg mb-2 whitespace-pre-wrap">{elicitation.title || elicitation.message || $i18n.t('Requires Input')}</h3>
		
		{#if elicitation.type === 'form' || elicitation.requestedSchema || elicitation.schema}
			<!-- JSON Schema Form Renderer (Primitive types only) -->
			<form on:submit|preventDefault={handleSubmit} class="space-y-4">
				{#each Object.entries(properties) as [key, prop]}
					<div class="flex flex-col gap-1">
						<label for={key} class="text-sm font-medium">
							{prop.title || key}
							{#if requiredFields.includes(key)}<span class="text-red-500">*</span>{/if}
						</label>
						
						{#if prop.description}
							<p class="text-xs text-gray-500">{prop.description}</p>
						{/if}

						{#if prop.enum}
							<select
								id={key}
								bind:value={formData[key]}
								required={requiredFields.includes(key)}
								class="p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
							>
								<option value="" disabled selected>Select an option</option>
								{#each prop.enum as option}
									<option value={option}>{option}</option>
								{/each}
							</select>
						{:else if prop.type === 'boolean'}
							<div class="flex items-center gap-2">
								<input
									type="checkbox"
									id={key}
									bind:checked={formData[key]}
									class="w-4 h-4 rounded border-gray-300"
								/>
								<label for={key} class="text-sm">Enable</label>
							</div>
						{:else if prop.type === 'number' || prop.type === 'integer'}
							<input
								type="number"
								id={key}
								bind:value={formData[key]}
								required={requiredFields.includes(key)}
								class="p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 w-full"
							/>
						{:else}
							<input
								type="text"
								id={key}
								bind:value={formData[key]}
								required={requiredFields.includes(key)}
								class="p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 w-full"
							/>
						{/if}
					</div>
				{/each}

				<div class="flex justify-end gap-2 mt-4">
					<button
						type="button"
						class="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition"
						on:click={() => resolveElicitation('cancel')}
						disabled={submitting}
					>
						{$i18n.t('Cancel')}
					</button>
					<button
						type="submit"
						class="px-4 py-2 bg-black text-white dark:bg-white dark:text-black hover:opacity-90 rounded-lg transition"
						disabled={submitting}
					>
						{$i18n.t('Submit')}
					</button>
				</div>
			</form>
		{:else if elicitation.type === 'url' || elicitation.url}
			<!-- URL Consent Form -->
			<div class="space-y-4">
				<p class="text-sm">{$i18n.t('This tool needs your authorization to continue. Please click the button below to authorize, then wait for completion or confirm when done.')}</p>
				<div class="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900/30 rounded-lg">
					<p class="text-xs text-gray-500 mb-1">Target URL</p>
					<p class="font-mono text-sm break-all">{elicitation.url}</p>
				</div>
				<div class="flex justify-between items-center mt-4">
					<button
						type="button"
						class="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition"
						on:click={() => resolveElicitation('decline')}
						disabled={submitting}
					>
						{$i18n.t('Decline')}
					</button>
					<div class="flex gap-2">
                        <a
                            href={elicitation.url}
                            target="_blank"
                            class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition text-center"
                        >
                            {$i18n.t('Open URL')}
                        </a>
						<button
							type="button"
							class="px-4 py-2 bg-black text-white dark:bg-white dark:text-black hover:opacity-90 rounded-lg transition"
							on:click={() => resolveElicitation('accept')}
							disabled={submitting}
						>
							{$i18n.t('Confirm Completed')}
						</button>
					</div>
				</div>
			</div>
		{/if}
	</div>
{/if}
