from __future__ import annotations
from typing import TYPE_CHECKING

import os
import yarl
import asyncio
import dateparser

import disnake
from disnake.ext import commands

import utils

if TYPE_CHECKING:
    from main import Okiyu

__all__ = ('GistContent', 'GithubClient',)


class GithubError(commands.CommandError):
    pass


class GistContent:
    def __init__(self, argument: str):
        try:
            block, code = argument.split('\n', 1)
        except ValueError:
            self.source = argument
            self.language = None
        else:
            if not block.startswith('```') and not code.endswith('```'):
                self.source = argument
                self.language = None
            else:
                self.language = block[3:]
                self.source = code.rstrip('`').replace('```', '')


class GithubClient:
    def __init__(self, bot: Okiyu) -> None:
        self.bot = bot
        self.lock = asyncio.Lock()

    async def github_request(self, method, url, *, params=None, data=None, headers=None) -> dict | str:
        hdrs = {
            'Accept': 'application/vnd.github.inertia-preview+json',
            'User-Agent': 'Okiyu',
            'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'
        }

        req_url = yarl.URL('https://api.github.com') / url

        if headers is not None and isinstance(headers, dict):
            hdrs.update(headers)

        await self.lock.acquire()
        try:
            async with self.bot.session.request(method, req_url, params=params, json=data, headers=hdrs) as r:
                remaining = r.headers.get('X-Ratelimit-Remaining')
                js = await r.json()
                if r.status == 429 or remaining == '0':
                    # wait before we release the lock
                    delta = disnake.utils._parse_ratelimit_header(r)
                    await asyncio.sleep(delta)
                    self.lock.release()
                    return await self.github_request(method, url, params=params, data=data, headers=headers)
                elif 300 > r.status >= 200:
                    return js
                else:
                    raise GithubError(js['message'])
        finally:
            if self.lock.locked():
                self.lock.release()

    async def create_gist(self, content, *, description=None, filename=None, public=True) -> str:
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }

        filename = filename or 'output.txt'
        data = {
            'public': public,
            'files': {
                filename: {
                    'content': content
                }
            }
        }

        if description:
            data['description'] = description

        js = await self.github_request('POST', 'gists', data=data, headers=headers)
        return js['html_url']

    async def get_user_info(self, username: str) -> disnake.Embed:
        """Tries to fetch the github data of an user and returns an embed with it.

        Parameters
        ----------
            username: :class:`str`
                The username of the user to search for on github.

        Returns
        -------
            :class:`disnake.Embed`
                The embed with the retrieved data.
        """

        try:
            data = await self.github_request('GET', 'users/' + username)
        except GithubError as e:
            em = disnake.Embed(
                title='Error!',
                description=''.join(e.args),
                color=utils.red
            )
            return em

        if data['name']:
            name = f'{data["name"]} ({data["login"]})'
        else:
            name = data['login']

        created_at = dateparser.parse(data['created_at'])

        em = disnake.Embed(
            title=name,
            color=utils.blurple,
            url=data['html_url'],
            timestamp=created_at,
        )
        if data['bio']:
            em.description = data['bio']

        em.set_footer(text='Joined')

        em.set_thumbnail(url=data['avatar_url'])

        em.add_field(
            name='Public Repos',
            value=data['public_repos'] or '0',
            inline=False,
        )

        if data['public_gists']:
            em.add_field(name='Public Gists', value=data['public_gists'], inline=False)

        value = [
            'Followers: ' + str(data['followers'])
            if data['followers']
            else 'Followers: 0'
        ]
        value.append(
            'Following: ' + str(data['following'])
            if data['following']
            else 'Following: 0'
        )

        em.add_field(name='Followers/Following', value='\n'.join(value), inline=False)

        if data['location']:
            em.add_field(name='Location', value=data['location'], inline=False)
        if data['company']:
            em.add_field(name='Company', value=data['company'], inline=False)
        if data['blog']:
            blog = data['blog']
            if blog.startswith('https://') or blog.startswith('http://'):
                pass
            else:
                blog = 'https://' + blog
            em.add_field(name='Website', value=blog, inline=False)

        return em

    async def get_repo_info(self, repo_name: str) -> disnake.Embed:
        """Tries to fetch the github data of a repository and returns an embed with it.

        Parameters
        ----------
            repo_name: :class:`str`
                The name of the repository to search for on github.

        Returns
        -------
            :class:`disnake.Embed`
                The embed with the retrieved data.
        """

        try:
            data = await self.github_request('GET', 'repos/' + repo_name)
        except GithubError as e:
            em = disnake.Embed(
                title='Error!',
                description=''.join(e.args),
                color=utils.red
            )
            return em

        created_at = dateparser.parse(data['created_at'])
        em = disnake.Embed(
            title=data['full_name'],
            color=utils.blurple,
            url=data['html_url'],
            timestamp=created_at,
        )

        # 2008-01-14T04:33:35Z

        em.set_footer(text='Created')

        owner = data['owner']

        em.set_author(
            name=owner['login'],
            url=owner['html_url'],
            icon_url=owner['avatar_url'],
        )
        em.set_thumbnail(url=owner['avatar_url'])

        description = data['description']
        if data['fork']:
            parent = data['parent']
            description = (
                f'Forked from [{parent["full_name"]}]({parent["html_url"]})\n\n' +
                description
            )

        if data['homepage']:
            description += '\n' + data['homepage']

        em.description = description

        em.add_field(name='Language', value=data['language'] or 'None')
        em.add_field(
            name='Stars', value=data['stargazers_count'] or '0', inline=False
        )
        em.add_field(
            name='Watchers', value=data['watchers_count'] or '0', inline=False
        )
        em.add_field(name='Forks', value=data['forks_count'] or '0', inline=False)

        return em
